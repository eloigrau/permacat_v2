from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import Proposal, ClarificationQuestion, Objection, ObjectionResponse, ProposalHistory
from . import services


# --- INLINES ---

class ClarificationQuestionInline(admin.TabularInline):
    model = ClarificationQuestion
    extra = 0
    readonly_fields = ('author', 'question', 'created_at')
    fields = ('author', 'question', 'answer', 'created_at')
    can_delete = True


class ObjectionResponseInline(admin.TabularInline):
    model = ObjectionResponse
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)


class ObjectionInline(admin.StackedInline):
    model = Objection
    extra = 0
    fields = ('author', 'description', 'is_valid_consent_objection', 'is_resolved', 'created_at')
    readonly_fields = ('created_at',)


class ProposalHistoryInline(admin.TabularInline):
    model = ProposalHistory
    extra = 0
    readonly_fields = ('content', 'reformulated_at')
    can_delete = False


# --- MODEL ADMINS ---

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
    'title', 'author', 'colored_status', 'unanswered_clarifications_count', 'active_objections_count', 'created_at')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('title', 'context', 'content')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ClarificationQuestionInline, ObjectionInline, ProposalHistoryInline]

    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'author', 'status', 'created_at', 'updated_at')
        }),
        ('Contenu de la Proposition', {
            'fields': ('context', 'content')
        }),
    )

    actions = ['action_advance_to_objections', 'action_check_and_advance_objections', 'action_reject_proposal']

    # --- INDICATEURS PERSONNALISÉS ---

    @admin.display(description='Statut')
    def colored_status(self, obj):
        colors = {
            Proposal.Status.DRAFT: 'secondary',
            Proposal.Status.CLARIFICATION: 'info',
            Proposal.Status.OBJECTION_ROUND: 'warning',
            Proposal.Status.OBJECTION_RESPONSE: 'warning',
            Proposal.Status.REFORMULATION: 'primary',
            Proposal.Status.ACCEPTED: 'success',
            Proposal.Status.REJECTED: 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span style="background-color: var(--bs-{color}, #6c757d); color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.get_status_display(),
            color=color
        )

    @admin.display(description='Clarifications en attente')
    def unanswered_clarifications_count(self, obj):
        count = obj.clarifications.filter(answer__isnull=True).count()
        if count > 0:
            return format_html('<b style="color: red;">{}</b>', count)
        return "0"

    @admin.display(description='Objections non résolues')
    def active_objections_count(self, obj):
        count = obj.objections.filter(is_resolved=False, is_valid_consent_objection=True).count()
        if count > 0:
            return format_html('<b style="color: orange;">{}</b>', count)
        return "0"

    # --- ACTIONS ADMIN ---

    @admin.action(description="Clôturer les clarifications -> Passer aux Objections")
    def action_advance_to_objections(self, request, queryset):
        success = 0
        for proposal in queryset:
            try:
                services.validate_clarifications(proposal)
                success += 1
            except ValidationError as e:
                self.message_user(request, f"Erreur sur '{proposal.title}': {e.message}", level='error')
        if success:
            self.message_user(request, f"{success} proposition(s) passée(s) en tour d'objections.")

    @admin.action(description="Analyser les objections -> Adopter ou Traiter")
    def action_check_and_advance_objections(self, request, queryset):
        for proposal in queryset:
            try:
                services.check_objections_and_advance(proposal)
                if proposal.status == Proposal.Status.ACCEPTED:
                    self.message_user(request, f"'{proposal.title}' a été ADOPTÉE par consentement !")
                else:
                    self.message_user(request, f"'{proposal.title}' passe au traitement des objections.")
            except ValidationError as e:
                self.message_user(request, f"Erreur sur '{proposal.title}': {e.message}", level='error')

    @admin.action(description="Rejeter définitivement la proposition")
    def action_reject_proposal(self, request, queryset):
        for proposal in queryset:
            services.reject_proposal(proposal)
        self.message_user(request, f"{queryset.count()} proposition(s) rejetée(s).")


@admin.register(Objection)
class ObjectionAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'author', 'is_valid_consent_objection', 'is_resolved', 'created_at')
    list_filter = ('is_valid_consent_objection', 'is_resolved', 'created_at')
    search_fields = ('description', 'proposal__title')
    inlines = [ObjectionResponseInline]


@admin.register(ClarificationQuestion)
class ClarificationQuestionAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'author', 'is_answered', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('question', 'answer', 'proposal__title')

    @admin.display(boolean=True, description='Répondu ?')
    def is_answered(self, obj):
        return bool(obj.answer)



# Register your models here.

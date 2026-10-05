from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.urls import reverse

from .models import Proposal, ClarificationQuestion, Objection, ObjectionResponse
from . import services
from .forms import ProposalClarificationEditForm, ProposalForm
from bourseLibre.utils import TestMembreAssoMixin, TestBureauAssoMixin, UserPassesTestMixin


class ProposalListView(TestMembreAssoMixin, ListView):
    model = Proposal
    template_name = 'gpc/proposal_list.html'
    context_object_name = 'proposals'
    ordering = ['-created_at']


    def get_queryset(self):
        if "asso" in self.request.GET and not "base" in self.request.GET:
            self.request.session["asso_slug"] = self.request.GET["asso"]
            qs = Proposal.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).filter(asso__slug=self.request.GET["asso"]).order_by("-updated_at")
        elif "asso_slug" in self.request.session and not "base" in self.request.GET:
            qs = Proposal.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).filter(asso__slug=self.request.session["asso_slug"]).order_by("-updated_at")
        else:
            qs = Proposal.objects.exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre()).order_by("-updated_at")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        context['asso_list'] = self.request.user.getListeSlugsNomsAssoEtPublic()
        return context


class ProposalDetailView(TestMembreAssoMixin, DetailView):
    model = Proposal
    template_name = 'gpc/proposal_detail.html'
    context_object_name = 'proposal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.object
        context['votes_count'] = proposal.resolution_votes.count()
        context['user_has_voted'] = proposal.resolution_votes.filter(voter=self.request.user).exists()
        # Formulaire d'édition pour la clarification (si auteur et phase clarification)
        if proposal.status == Proposal.Status.CLARIFICATION and self.request.user == proposal.author:
            context['edit_form'] = ProposalClarificationEditForm(instance=proposal)
        return context

class ProposalCreateView(LoginRequiredMixin, CreateView):
    model = Proposal
    form_class = ProposalForm
    template_name = 'gpc/create_proposal.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        services.submit_proposal(self.object)
        messages.success(self.request, "Proposition créée et soumise pour clarification.")
        return response

    def get_success_url(self):
        return reverse('gpc:proposal_detail', kwargs={'pk': self.object.pk})


class EditProposalClarificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vue permettant à l'auteur d'éditer la proposition pendant la clarification."""
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        form = ProposalClarificationEditForm(request.POST, instance=proposal)
        if form.is_valid():
            try:
                services.update_proposal_in_clarification(
                    proposal,
                    form.cleaned_data['title'],
                    form.cleaned_data['context'],
                    form.cleaned_data['content']
                )
                messages.success(request, "La proposition a été mise à jour.")
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, "Formulaire invalide.")
        return redirect('gpc:proposal_detail', pk=proposal.pk)

class AddClarificationView(TestMembreAssoMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        question_text = request.POST.get('question', '').strip()
        if question_text:
            ClarificationQuestion.objects.create(
                proposal=proposal,
                author=request.user,
                question=question_text
            )
            messages.success(request, "Question transmise.")
        return redirect('gpc:proposal_detail', pk=proposal.pk)


class AnswerClarificationView(TestMembreAssoMixin, View):
    def test_func(self):
        res = super().test_func()
        if res:
            question = get_object_or_404(ClarificationQuestion, pk=self.kwargs['question_id'])
            return self.request.user == question.proposal.author
        return False

    def post(self, request, question_id):
        question = get_object_or_404(ClarificationQuestion, pk=question_id)
        answer_text = request.POST.get('answer', '').strip()
        if answer_text:
            question.answer = answer_text
            question.save()
            messages.success(request, "Réponse enregistrée.")
        return redirect('gpc:proposal_detail', pk=question.proposal.pk)


class CloseClarificationsView(TestMembreAssoMixin, View):
    def test_func(self):
        res = super().test_func()
        if res:
            proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
            return self.request.user == proposal.author
        return False

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        try:
            services.close_clarifications(proposal)
            messages.success(request, "Clarifications closes. Passage au tour d'objections.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('gpc:proposal_detail', pk=proposal.pk)


class AddObjectionView(TestMembreAssoMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        description = request.POST.get('description', '').strip()
        if description:
            Objection.objects.create(
                proposal=proposal,
                author=request.user,
                description=description
            )
            messages.warning(request, "Objection enregistrée.")
        return redirect('gpc:proposal_detail', pk=proposal.pk)

class VoteResolveObjectionView(LoginRequiredMixin, View):
    """Enregistre le vote d'un membre pour la levée d'une objection."""
    def post(self, request, objection_id):
        objection = get_object_or_404(Objection, pk=objection_id)
        approve = request.POST.get('approve') == 'true'

        try:
            is_now_resolved = services.vote_to_resolve_objection(objection, request.user, approve=approve)
            if is_now_resolved:
                messages.success(request, "Vote enregistré ! Le seuil de votes est atteint : l'objection est désormais levée.")
            else:
                messages.info(request, f"Vote enregistré. ({objection.positive_votes_count}/3 votes requis pour lever l'objection).")
        except ValidationError as e:
            messages.error(request, e.message)

        return redirect('gpc:proposal_detail', pk=objection.proposal.pk)

class CloseObjectionsView(TestMembreAssoMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        try:
            services.close_objections(proposal)
            if proposal.status == Proposal.Status.ACCEPTED:
                messages.success(request, "Aucune objection bloquante. Proposition adoptée par consentement !")
            else:
                messages.info(request, "Objections à traiter. Passage en délibération.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('gpc:proposal_detail', pk=proposal.pk)


class AddObjectionResponseView(TestMembreAssoMixin, View):
    def post(self, request, objection_id):
        objection = get_object_or_404(Objection, pk=objection_id)
        content = request.POST.get('content', '').strip()
        if content:
            ObjectionResponse.objects.create(
                objection=objection,
                author=request.user,
                content=content
            )
            messages.info(request, "Piste de solution ajoutée.")
        return redirect('gpc:proposal_detail', pk=objection.proposal.pk)


class ResolveObjectionView(TestMembreAssoMixin, UserPassesTestMixin, View):
    """Permet à l'auteur de l'objection ou à l'auteur de la proposition de lever l'objection."""
    def test_func(self):
        objection = get_object_or_404(Objection, pk=self.kwargs['objection_id'])
        return self.request.user in [objection.author, objection.proposal.author]

    def post(self, request, objection_id):
        objection = get_object_or_404(Objection, pk=objection_id)
        services.resolve_objection(objection, request.user)
        messages.success(request, "L'objection a été marquée comme levée.")
        return redirect('gpc:proposal_detail', pk=objection.proposal.pk)


class CloseDeliberationView(TestMembreAssoMixin, UserPassesTestMixin, View):
    """Clôture la délibération et valide la proposition si toutes les objections sont levées."""
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        try:
            services.close_deliberation(proposal)
            messages.success(request, "Délibération close. La proposition est officiellement adoptée par consentement !")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('gpc:proposal_detail', pk=proposal.pk)


class ReformulateProposalView(TestMembreAssoMixin, UserPassesTestMixin, View):
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def get(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        return render(request, 'gpc/reformulate.html', {'proposal': proposal})

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        new_content = request.POST.get('content', '').strip()
        try:
            services.reformulate_proposal(proposal, new_content)
            messages.success(request, "Proposition reformulée. Un nouveau tour d'objections est ouvert.")
            return redirect('gpc:proposal_detail', pk=proposal.pk)
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('gpc:proposal_detail', pk=proposal.pk)


class RejectProposalView(TestMembreAssoMixin, UserPassesTestMixin, View):
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        services.reject_proposal(proposal)
        messages.error(request, "La proposition a été classée comme rejetée.")
        return redirect('gpc:proposal_detail', pk=proposal.pk)


# views.py
class VoteDeliberationView(TestMembreAssoMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        try:
            services.cast_validation_vote(proposal, request.user)
            messages.success(request, "Votre vote de validation a été pris en compte.")
        except ValidationError as e:
            messages.error(request, e.message)

        return redirect('gpc:proposal_detail', pk=proposal.pk)
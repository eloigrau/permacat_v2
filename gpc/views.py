from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.urls import reverse

from .models import Proposal, ClarificationQuestion, Objection, ObjectionResponse
from . import services


class ProposalListView(LoginRequiredMixin, ListView):
    model = Proposal
    template_name = 'gpc/proposal_list.html'
    context_object_name = 'proposals'
    ordering = ['-created_at']


class ProposalDetailView(LoginRequiredMixin, DetailView):
    model = Proposal
    template_name = 'gpc/proposal_detail.html'
    context_object_name = 'proposal'


class ProposalCreateView(LoginRequiredMixin, CreateView):
    model = Proposal
    fields = ['title', 'context', 'content']
    template_name = 'gpc/create_proposal.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        services.submit_proposal(self.object)
        messages.success(self.request, "Proposition créée et soumise pour clarification.")
        return response

    def get_success_url(self):
        return reverse('gpc:proposal_detail', kwargs={'pk': self.object.pk})


class AddClarificationView(LoginRequiredMixin, View):
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


class AnswerClarificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        question = get_object_or_404(ClarificationQuestion, pk=self.kwargs['question_id'])
        return self.request.user == question.proposal.author

    def post(self, request, question_id):
        question = get_object_or_404(ClarificationQuestion, pk=question_id)
        answer_text = request.POST.get('answer', '').strip()
        if answer_text:
            question.answer = answer_text
            question.save()
            messages.success(request, "Réponse enregistrée.")
        return redirect('gpc:proposal_detail', pk=question.proposal.pk)


class CloseClarificationsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        try:
            services.close_clarifications(proposal)
            messages.success(request, "Clarifications closes. Passage au tour d'objections.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('gpc:proposal_detail', pk=proposal.pk)


class AddObjectionView(LoginRequiredMixin, View):
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


class CloseObjectionsView(LoginRequiredMixin, View):
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


class AddObjectionResponseView(LoginRequiredMixin, View):
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


class ResolveObjectionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Permet à l'auteur de l'objection ou à l'auteur de la proposition de lever l'objection."""
    def test_func(self):
        objection = get_object_or_404(Objection, pk=self.kwargs['objection_id'])
        return self.request.user in [objection.author, objection.proposal.author]

    def post(self, request, objection_id):
        objection = get_object_or_404(Objection, pk=objection_id)
        services.resolve_objection(objection)
        messages.success(request, "L'objection a été marquée comme levée.")
        return redirect('gpc:proposal_detail', pk=objection.proposal.pk)


class CloseDeliberationView(LoginRequiredMixin, UserPassesTestMixin, View):
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


class ReformulateProposalView(LoginRequiredMixin, UserPassesTestMixin, View):
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


class RejectProposalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        proposal = get_object_or_404(Proposal, pk=self.kwargs['pk'])
        return self.request.user == proposal.author

    def post(self, request, pk):
        proposal = get_object_or_404(Proposal, pk=pk)
        services.reject_proposal(proposal)
        messages.error(request, "La proposition a été classée comme rejetée.")
        return redirect('gpc:proposal_detail', pk=proposal.pk)
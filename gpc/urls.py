from django.urls import path
from . import views

app_name = "gpc"

urlpatterns = [
    # Navigation générale
    path('', views.ProposalListView.as_view(), name='proposal_list'),
    path('creer/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('<int:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),

    # Phase Clarifications
    path('<int:pk>/clarifier/', views.AddClarificationView.as_view(), name='add_clarification'),
    path('clarification/<int:question_id>/repondre/', views.AnswerClarificationView.as_view(),
         name='answer_clarification'),
    path('<int:pk>/cloturer-clarifications/', views.CloseClarificationsView.as_view(), name='close_clarifications'),

    # Phase Objections
    path('<int:pk>/objecter/', views.AddObjectionView.as_view(), name='add_objection'),
    path('<int:pk>/cloturer-objections/', views.CloseObjectionsView.as_view(), name='close_objections'),

    # Phase Délibération & Levée
    path('objection/<int:objection_id>/repondre/', views.AddObjectionResponseView.as_view(),
         name='add_objection_response'),
    path('objection/<int:objection_id>/voter-levee/', views.VoteResolveObjectionView.as_view(),
         name='vote_resolve_objection'),
    path('<int:pk>/cloturer-deliberation/', views.CloseDeliberationView.as_view(), name='close_deliberation'),

    # Actions Auteur
    path('<int:pk>/reformuler/', views.ReformulateProposalView.as_view(), name='reformulate_proposal'),
    path('<int:pk>/rejeter/', views.RejectProposalView.as_view(), name='reject_proposal'),
]

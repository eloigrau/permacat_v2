from django.urls import path
from .views import DashboardView

app_name = 'dashboard'


urlpatterns = [
    path(
        "",
        DashboardView.as_view(template_name="dashboard_analytics.html"),
        name="index",
    )
]

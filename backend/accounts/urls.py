from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("platform/login/", views.PlatformLoginView.as_view()),
    path("school/login/", views.SchoolLoginView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("change-password/", views.ChangePasswordView.as_view()),
    path("me/", views.MeView.as_view()),
    path("platform/ping/", views.PlatformPingView.as_view()),
    path("school/ping/", views.SchoolPingView.as_view()),
    path("finance-check/", views.FinanceCheckView.as_view()),
    path("marks-check/", views.MarksCheckView.as_view()),
]
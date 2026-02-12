from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from templates_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.landing_page, name="landing"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("templates/", include("templates_app.urls")),
]

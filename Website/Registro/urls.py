#coding=utf-8
from pathlib import Path

from django.shortcuts import render
from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views
from .forms import PasswordResetForm

### COMMON PATTERNS ###
urlpatterns = [
    path('', views.index_view, name='index'),
    path('signup_volun', views.signup_volun, name='signup_volun'),
    path('signup_org', views.signup_org, name='signup_org'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),

    path('eventos', views.active_events, name='home'),
    path('eventos-archivados', views.old_events, name='old_events'),
    path('eventos/<str:pk>', views.event_details, name='event_details'),

    path('organizadores/<str:pk>', views.org_details, name='org_details'),

    path('voluntarios/<str:pk>', views.volun_details, name='volun_details'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
]

### ORGANIZADOR ONLY ###
urlpatterns += [
    path('mis-eventos', views.my_events, name='my_events'),
    path('crear-evento', views.EventCreateView.as_view(), name='new_event'),
    path('eventos/<str:pk>/edit', views.EventEditView.as_view(), name='edit_event'),
    path('eventos/<str:pk>/inscritos', views.event_participations,
         name='event_participations'),
    path('eventos/<str:pk>/editar_inscritos', views.edit_participations,
         name='edit_participations'),
]

### PASSWORD RESET URLS ###
PASS_RESET_DIR = Path("PasswordReset")
urlpatterns += [
    path("password_reset/",
         auth_views.PasswordResetView.as_view(
            form_class=PasswordResetForm,
            template_name=str(PASS_RESET_DIR/"reset_form.html"),
            email_template_name=str(PASS_RESET_DIR/"email.html"),
            subject_template_name=str(PASS_RESET_DIR/"subject.txt"),
            success_url=reverse_lazy("password_reset_done")),
        name='password_reset'),

    path("password_reset/done",
         auth_views.PasswordResetDoneView.as_view(template_name=str(PASS_RESET_DIR/"reset_done.html")),
         name='password_reset_done'),

    re_path(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(
                template_name=str(PASS_RESET_DIR/"reset_confirm.html"),
                success_url=reverse_lazy("password_reset_complete")),
            name="password_reset_confirm"),

    path("password_reset/complete",
         auth_views.PasswordResetCompleteView.as_view(
            template_name=str(PASS_RESET_DIR/"reset_complete.html")),
        name="password_reset_complete"),
]

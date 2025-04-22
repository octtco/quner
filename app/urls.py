from django.contrib import admin
from django.urls import path, include

from app import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("comments/", views.comments, name="comments"),
    path("addcomments/<int:id>", views.addcomments, name="addcomments"),
    path("", views.dashboard, name="home"),
]

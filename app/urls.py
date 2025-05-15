from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("comments/", views.comments, name="comments"),
    path("addcomments/<int:id>", views.addcomments, name="addcomments"),
    # 添加个人信息页面的 URL
    path("personaldetails/", views.personal_details, name="personaldetails"),
    path("cityLevelAnalysis/", views.cityLevelAnalysis, name="cityLevelAnalysis"), # 更新城市与景点等级分析页面的 URL
    path("priceAnalysis/", views.priceAnalysis, name="priceAnalysis"),
    path("userActicityAnalysis/", views.userActivityAnalysis, name="userActivityAnalysis"),
    path("recommendation/", views.recommendation, name="recommendation"),
    path('detailIntroCloud/', views.detailIntroCloud, name='detailIntroCloud'),
    path('commentContentCloud/', views.commentContentCloud, name='commentContentCloud'),
    path("", views.dashboard, name="home"),
]

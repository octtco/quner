from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("comments/", views.comments, name="comments"),
    path("addcomments/<int:id>", views.addcomments, name="addcomments"),
    # 添加个人信息页面的 URL
    path("personaldetails/", views.personal_details, name="personaldetails"),
    path("cityLevelAnalysis/", views.cityLevelAnalysis, name="cityLevelAnalysis"), # 更新城市与景点等级分析页面的 URL
    # 添加新页面的 URL
    path("priceAnalysis/", views.priceAnalysis, name="priceAnalysis"),
    # path("salesVolumeAnalysis/", views.sales_volume_analysis, name="salesVolumeAnalysis"),
    path("recommendation/", views.recommendation, name="recommendation"),
    path("", views.dashboard, name="home"),
]

from django.urls import path
from .views import AdminLogin,UnblockUser,BlockUser

urlpatterns = [
    path('adminlogin/', AdminLogin.as_view()), 
    path('blockuser/<int:pk>/', BlockUser.as_view()),
    path('unblockuser/<int:pk>/', UnblockUser.as_view()),       
]
from django.urls import path
from .views import AdminLogin,UnblockUser,BlockUser,Deleteunregisteredusers

urlpatterns = [
    path('adminlogin/', AdminLogin.as_view()), 
    path('blockuser/<int:pk>/', BlockUser.as_view()),
    path('unblockuser/<int:pk>/', UnblockUser.as_view()),  
    path('deleteunregisteredusers/', Deleteunregisteredusers.as_view()),      
]
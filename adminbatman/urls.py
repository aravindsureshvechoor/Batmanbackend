from django.urls import path
from .views import AdminLogin

urlpatterns = [
    path('adminlogin/', AdminLogin.as_view()), 
          
]
from django.urls import path
from .views import Signup,UserLogin

urlpatterns = [
    path('signup/', Signup.as_view()), 
    path('userlogin/', UserLogin.as_view()),       
]
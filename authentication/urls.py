from django.urls import path
from .views import Signup,UserLogin,GoogleAuth

urlpatterns = [
    path('signup/', Signup.as_view()), 
    path('userlogin/', UserLogin.as_view()),
    path('googleauth/', GoogleAuth.as_view()),       
]
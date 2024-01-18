from django.urls import path
from .views import Signup,UserLogin,GoogleAuth,UserLogoutView

urlpatterns = [
    path('signup/', Signup.as_view()), 
    path('userlogin/', UserLogin.as_view()),
    path('googleauth/', GoogleAuth.as_view()),
    path('userlogout/', UserLogoutView.as_view()),      
]
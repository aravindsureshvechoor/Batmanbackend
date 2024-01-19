from django.urls import path
from .views import Signup,UserLogin,GoogleAuth,VerifyOTP

urlpatterns = [
    path('signup/', Signup.as_view()), 
    path('userlogin/', UserLogin.as_view()),
    path('googleauth/', GoogleAuth.as_view()),
    path('verifyotp/', VerifyOTP.as_view()),    
]
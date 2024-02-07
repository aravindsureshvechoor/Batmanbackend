from django.urls import path
from .views import (Signup,UserLogin,GoogleAuth,VerifyOTP,Retrieveuserdetails,FollowView,FollowListView,
FollowerListView,UserStatus,UserRetrieveView,UserPostRetrieve,PeopleYouMayKnow)

urlpatterns = [
    path('signup/', Signup.as_view()), 
    path('userlogin/', UserLogin.as_view()),
    path('googleauth/', GoogleAuth.as_view()),
    path('verifyotp/', VerifyOTP.as_view()),
    path('userdetailsforadmin/',Retrieveuserdetails.as_view()),
    path('follow/<str:email>/',FollowView.as_view()),   
    path('following/', FollowListView.as_view(), name='following'),
    path('followers/', FollowerListView.as_view(), name='followers'),
    path('userstatus/<str:email>/',UserStatus.as_view(),name='userstatus'),
    path('retrieveuser/<str:email>/',UserRetrieveView.as_view(),name='retrieveuser'),
    path('retrieveuserpost/<str:email>/',UserPostRetrieve.as_view(),name='retrieveuserpost'),
    path('peopleyoumayknow/',PeopleYouMayKnow.as_view(),name='peopleyoumayknow'),

]
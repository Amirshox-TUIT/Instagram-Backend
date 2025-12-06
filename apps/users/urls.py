from django.urls import path

from apps.users.views import register, login, search, followings, profile

app_name = 'users'

urlpatterns = [
    path('register/', register.RegisterAPIView.as_view(), name='register'),
    path('login/', login.LoginAPIView.as_view(), name='login'),
    path('logout/', login.LogoutAPIView.as_view(), name='logout'),
    path('search/', search.SearchUserAPIView.as_view(), name='search'),
    path('followings/<str:username>/', followings.UserFollowingsAPIView.as_view(), name='followings'),
    path('<str:username>/unfollow/', followings.FollowUnfollowUserAPIView.as_view(), name='unfollow'),
    path('<str:username>/follow/', followings.FollowUnfollowUserAPIView.as_view(), name='follow'),
    path('u/<str:username>/', profile.ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:pk>/', profile.UserProfileUpdateAPIView.as_view(), name='profile-detail'),

]
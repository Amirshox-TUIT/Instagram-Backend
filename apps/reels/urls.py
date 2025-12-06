from django.urls import path

from apps.reels import views

app_name = 'reels'

urlpatterns = [
    path('', views.ReelListCreateAPIView.as_view(), name='list'),
    path('<int:pk>/', views.ReelRetrieveUpdateDestroyAPIView.as_view(), name='detail'),
    path('<int:pk>/comments/', views.ReelCommentListCreateAPIView.as_view(), name='comments'),
    path('<int:pk>/comments/<int:comment_id>/', views.ReelCommentRetrieveUpdateDestroyAPIView.as_view(), name='comments-detail'),
    path('<int:pk>/like/', views.ReelLikeAPIView.as_view(), name='like'),
    path('u/<str:username>/', views.UserReelsListAPIView.as_view(), name='users'),
]
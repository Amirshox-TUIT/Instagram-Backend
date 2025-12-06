from django.urls import path

from apps.posts.views import post_list, post_create, comments
from apps.posts.views.my_posts import MyPostsListAPIView
from apps.posts.views.post_list import UserArticleListView

app_name = "posts"

urlpatterns = [
    path('timeline/', post_list.TimelineAPIView.as_view(), name='timeline'),
    path('create/', post_create.CreatePostAPIView.as_view(), name='create-post'),
    path('<int:id>/', post_list.PostRetrieveUpdateDestroyAPIView.as_view(), name='detail'),
    path('<int:post_id>/like/', post_list.PostLikeAPIView.as_view(), name='like'),
    path('my_posts/', MyPostsListAPIView.as_view(), name='my-posts'),
    path('u/<str:username>/', UserArticleListView.as_view(), name='user-articles'),
    path('comments/', comments.CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:post_id>/', comments.PostCommentsListView.as_view(), name='post-comments'),
    path('comments/delete/<int:comment_id>/', comments.CommentUpdateDeleteView.as_view(), name='comment-detail'),
    path('comments/update/<int:comment_id>/', comments.CommentUpdateDeleteView.as_view(), name='comment-detail'),
]
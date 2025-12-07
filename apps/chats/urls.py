from django.urls import path
from .views import MessageListCreateAPIView, MessageRetrieveUpdateDestroyAPIView, ChatListAPIView, \
    UnreadMessagesCountAPIView

app_name = 'chats'

urlpatterns = [
    path('unread-count/', UnreadMessagesCountAPIView.as_view(), name='unread-count'),
    path('<str:username>/', MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('detail/<int:pk>/', MessageRetrieveUpdateDestroyAPIView.as_view(), name='message-detail'),
    path('', ChatListAPIView.as_view(), name='chat-list'),

]
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Reel(models.Model):
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reels')
    likes = models.ManyToManyField(User, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.username}-{self.content}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reel'
        verbose_name_plural = 'Reels'



class ReelsComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reel_comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}-{self.text}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reel Comment'
        verbose_name_plural = 'Reel Comments'
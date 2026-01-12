from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    # 投稿内容
    content = models.TextField()
    # 投稿日時（自動追加）
    created_at = models.DateTimeField(auto_now_add=True)
    # 投稿者（ユーザーモデルと紐付け、ユーザー削除時に道連れ削除）
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f'{self.author.username}: {self.content[:20]}'
    
    def total_likes(self):
        return self.likes.count()
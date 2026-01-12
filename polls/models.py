from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title= models.CharField(max_length=200)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey(User,on_delete=models.CASCADE,)
    likes=models.ManyToManyField(User,related_name="likes", blank=True)
    
    

    def __str__(self):
        return self.title
    
    
    def total_likes(self):
        return self.likes.count()
    



    




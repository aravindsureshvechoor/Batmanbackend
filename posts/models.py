from django.db import models
from authentication.models import User



# Create your models here.
def upload_post(instance, filename):
    return 'posts/{filename}'.format(filename=filename)

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_img = models.ImageField(upload_to=upload_post)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        if self.caption is not None:
            return self.caption 

    def total_likes(self):
        return self.likes.count()

class Reportedposts(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post   = models.ForeignKey(Post, on_delete=models.CASCADE) 

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.body, self.user.first_name)


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  
    class Meta:
        unique_together = ('user', 'post')  

    def __str__(self):
        return f"{self.user.email} saved {self.post.id}"  

class Notification(models.Model):
   NOTIFICATION_TYPES = [
        ('like', 'New Like'),
        ('post', 'New Post'),
        ('follow', 'New Follow'),
        ('comment', 'New Comment'),
        ('blocked', 'Post Blocked'),
    ]
   
   to_user = models.ForeignKey(User, related_name="notification_to", on_delete=models.CASCADE, null=True)
   from_user = models.ForeignKey(User, related_name="notification_from", on_delete=models.CASCADE, null=True)
   notification_type = models.CharField(choices=NOTIFICATION_TYPES, max_length=20)
   post  = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
   comment  = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
   created = models.DateTimeField(auto_now_add=True)
   is_seen = models.BooleanField(default=False)
   
   def __str__(self):
        return f"{self.from_user} sent a {self.notification_type} notification to {self.to_user}"
    

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
    reported_by_users = models.ManyToManyField(User, related_name='reported_posts', blank=True)

    def __str__(self):
        return self.caption

    def total_reports(self):
        return self.reported_by_users.count()

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.body, self.user.first_name)


class Follow(models.Model):
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.follower} follows {self.following}"
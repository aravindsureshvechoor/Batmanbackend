from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from .managers import UserAccountManager


def upload_to(instance, filename):
    return 'profile/{filename}'.format(filename=filename)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True, null=True, upload_to=upload_to,default='user.png')
    gender = models.CharField(max_length=50)
    is_online = models.BooleanField(default=False)
    set_interest = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    otp = models.CharField(max_length=4,null=True)
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        related_query_name="custom_user_group",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        related_query_name="custom_user_permission",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.first_name
    
    def get_follower_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()



class Follow(models.Model):
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.follower} follows {self.following}"


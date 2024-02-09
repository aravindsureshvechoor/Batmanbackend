from django.contrib import admin

# Register your models here.
from . models import Post,Notification

admin.site.register(Post)
admin.site.register(Notification)
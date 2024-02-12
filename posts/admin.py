from django.contrib import admin

# Register your models here.
from . models import Post,Notification,Reportedposts

admin.site.register(Post)
admin.site.register(Notification)
admin.site.register(Reportedposts)
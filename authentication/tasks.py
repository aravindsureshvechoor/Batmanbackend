# tasks.py

from celery import Celery
from celery import shared_task
from django.core.mail import send_mail

app = Celery('batman')  # Replace 'your_project' with your actual Django project name

@shared_task
def welcomemail(email):
    subject = "Successfully Registered"
    sendermail = "Batman Community"
    message = "Congrats! You are now part of 'The Batman Community'"
    send_mail(subject, message, sendermail, [email])

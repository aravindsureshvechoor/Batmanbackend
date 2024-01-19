# tasks.py

from celery import Celery
from celery import shared_task
from django.core.mail import send_mail
import random

app = Celery('batman')  # Replace 'your_project' with your actual Django project name

@shared_task
def welcomemail(email):
    subject = "Successfully Registered"
    sendermail = "Batman Community"
    message = "Congrats! You are now part of 'The Batman Community'"
    send_mail(subject, message, sendermail, [email])

@shared_task
def otp(email):
     #setting otp in the session and sending it to the user
    randomotp = str(random.randint(1000, 9999))
    
    subject = "OTP"
    sendermail = "Batman Community"
    otp = f"{randomotp}"
    send_mail(subject,otp,sendermail,[email])
    return randomotp

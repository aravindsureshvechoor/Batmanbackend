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
def otp(email, subject="OTP", sender_name="Batman Community"):
    random_otp = str(random.randint(1000, 9999))
 
    message = f"Your one-time password is: {random_otp}"

    try:
        send_mail(subject, message, sender_name, [email])
        return random_otp
    except Exception as e:
        # Handle email sending failure
        print(f"Failed to send OTP email to {email}. Error: {str(e)}")
        return None

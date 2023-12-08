from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User, EmailTemplate
from twilio.rest import Client
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
import pyotp
import base64
import os
from django.utils import timezone
import pytz
from django.template.loader import render_to_string

current_timezone = settings.TIME_ZONE


def send_otp_via_mail(email, username, type):
    email_otp_template = EmailTemplate.objects.filter(type='otp').first()

    subject = email_otp_template.subject
    print(f"EMAIL USERNAME:{username}")
    # Replace placeholders in the subject
    subject = subject.replace("{{company_name}}", "Dating App")

    # Generate OTP
    otp = str(random.randint(1000, 9999))

    # Replace placeholders in the HTML template
    html_content = email_otp_template.content.replace("{{username}}", username.capitalize()).replace("{{otp}}", otp).replace("{{support_email}}","support@dating.com")
    # html_content = html_content.replace("{{company_name}}", "Dating App")
    # html_content = content.replace("{{otp}}", otp)

    # Send email with both plain text and HTML content
    email_from = settings.EMAIL_HOST
    send_mail(
        subject,
        f"Hello {username.capitalize()},\nEnter this code {otp} in the login section of the Dating app to securely access your account.",
        email_from,
        [email],
        html_message=html_content
    )

    user_obj = User.objects.filter(email = email).first()
    if type == 'login':
        if user_obj.has_2fa_enabled:
            user_obj.login_otp = otp
            print(f"current timezone:{current_timezone}")

            now = settings.NOW
            print(f"current time:{now}")
            user_obj.login_otp_validity = now + timedelta(minutes=1) # Set the validity for 5 minute
    else:
        user_obj.otp = otp
    user_obj.save()
    
def send_forgot_password_mail(subject, message, email_from, email, html_content):
    email_from = settings.EMAIL_HOST
    send_mail(
        subject,
        '',
        email_from,
        [email],
        html_message=html_content
    )

    
    
    
    
def send_otp_whatsapp():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER
    to = 'whatsapp:+919497347484'  # Correct WhatsApp number format
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(to=to, from_='whatsapp:' + twilio_phone_number, body='WhatsApp OTP testing')

    
    return (f"OTP sent to {to} successfully: {message.sid}")

    

def verify_otp(user_id, otp, type):
    if type == 'login':
        user = User.objects.get(id = user_id)
        print(f"otp:{otp}")
        if user.login_otp != otp:
            return Response(f"OTP is invalid", status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':'success','message':'Login otp verification successful'}, status=status.HTTP_200_OK)
        

    # return(f"OTP ")
    
    
def welcome_email(email, username, type):
    email_otp_template = EmailTemplate.objects.filter(type='register').first()

    subject = email_otp_template.subject.replace("{{company_name}}", "DatingApp")
    print(f"EMAIL USERNAME:{username}")
    # Replace placeholders in the subject


    # Replace placeholders in the HTML template
    html_content = email_otp_template.content.replace("{{username}}", username).replace("{{company_name}}", "DatingApp").replace("{{support_email}}", "support@dating.com")
    # html_content = html_content.replace("{{company_name}}", "Dating App")
    # html_content = content.replace("{{otp}}", otp)

    # Send email with both plain text and HTML content
    email_from = settings.EMAIL_HOST
    send_mail(
        subject,
       "Welcome",
        email_from,
        [email],
        html_message=html_content
    )

   
from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User
from twilio.rest import Client
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
import pyotp
import base64
import os

def send_otp_via_mail(email, type):
    subject = 'Your account verification email'
    otp = random.randint(1000,9999)
    message = f'Your otp is for dating app verification {otp}'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])

    user_obj = User.objects.filter(email = email).first()
    if type == 'login':
        if user_obj.has_2fa_enabled:
            otp = generate_login_otp(email=email)
            user_obj.login_otp = otp
            user_obj.login_otp_validity = datetime.now() + timedelta(minutes=1) # Set the validity for 5 minutes
        return True
    else:
        user_obj.otp = otp
    user_obj.save()

def send_otp_whatsapp():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER
    to = 'whatsapp:+919497347484'  # Correct WhatsApp number format
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(to=to, from_='whatsapp:' + twilio_phone_number, body='WhatsApp OTP testing')

    
    return (f"OTP sent to {to} successfully: {message.sid}")
def enable_tfa(user):
    user = User.objects.filter(username = user).first()
    secret_bytes = os.urandom(10) # Generate a random 80-bit (10-byte) secret
    shared_secret = base64.b32encode(secret_bytes).decode()
    print(f"shared secret = {shared_secret}")
    user.shared_secret = shared_secret
    user.two_step_verification = True
    user.save()
    
def generate_login_otp(email):
    user = User.objects.filter(email = email).first()
    shared_secret = user.shared_secret
    totp = pyotp.TOTP(shared_secret)
    otp = totp.now()
    return otp

def verify_otp(user_id, otp, type):
    if type == 'login':
        user = User.objects.get(id = user_id)
        print(f"otp:{otp}")
        if user.login_otp != otp:
            return Response(f"OTP is invalid", status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':'success','message':'Login otp verification successful'}, status=status.HTTP_200_OK)
        

    # return(f"OTP ")
from django.core.mail import send_mail, get_connection, BadHeaderError
import random
from django.conf import settings
from .models import User, EmailTemplate, Configurations
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

company_details = company_name = company_mail = email_host = email_port = email_host_user = email_host_password = email_tls = "sa" 

current_timezone = settings.TIME_ZONE
def mail_conf():

    try:
        company_details = Configurations.objects.first()
        company_name = company_details.company_name
        company_mail = company_details.company_mail
        welcome_mail = company_details.welcome_mail
        email_host = company_details.email_host,
        email_port = company_details.email_port,
        email_host_user = company_details.email_host_user,
        email_host_password = company_details.email_host_password,
        email_tls = company_details.email_tls

        return {'company_name':company_name,
                'company_mail':company_mail,
                'welcome_mail':welcome_mail,
                'email_host':email_host,
                'email_port':email_port,
                'email_host_user':email_host_user,
                'email_host_password':email_host_password,
                'email_tls':email_tls,
                }
    except Configurations.DoesNotExist:
        
        pass

def get_email_connection(email_host, email_port, email_host_user, email_host_password, email_tls):
    # Specify port in the connection
    connection = get_connection(
        # host=email_host,
        # port=587,  # Your specific port
        # username=email_host_user,
        # password=email_host_password,
        # use_tls=True,
        host=email_host,
        port=email_port,  # Your specific port
        username=email_host_user,
        password=email_host_password,
        use_tls=True,
    )
    return connection
def send_otp_via_mail(email, username, type):
    email_otp_template = EmailTemplate.objects.filter(type='otp').first()

    subject = email_otp_template.subject
    print(f"EMAIL USERNAME:{username}")
    # Replace placeholders in the subject
    subject = subject.replace("{{company_name}}", f"{company_name}")

    # Generate OTP
    otp = str(random.randint(1000, 9999))

    # Replace placeholders in the HTML template
    html_content = email_otp_template.content.replace("{{username}}", username.capitalize()).replace("{{otp}}", otp).replace("{{support_email}}",f"{company_mail}")
    # html_content = html_content.replace("{{company_name}}", "Dating App")
    # html_content = content.replace("{{otp}}", otp)

    # Send email with both plain text and HTML content
        
    mail_details = mail_conf()
    connection = get_email_connection(email_host = mail_details['email_host'][0], 
                                email_port = mail_details['email_port'][0],
                                email_host_user = mail_details['email_host_user'][0],
                                email_host_password = mail_details['email_host_password'][0],
                                email_tls= mail_details['email_tls'])
    send_mail(
        subject,
        f"Hello {username.capitalize()},\nEnter this code {otp} in the login section of the Dating app to securely access your account.",
        email_host[0],
        [email],
        html_message=html_content,
        connection=connection,
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
    
    mail_details = mail_conf()
    connection = get_email_connection(email_host = mail_details['email_host'][0], 
                                email_port = mail_details['email_port'][0],
                                email_host_user = mail_details['email_host_user'][0],
                                email_host_password = mail_details['email_host_password'][0],
                                email_tls= mail_details['email_tls'])

    send_mail(
        subject,
        '',
        email_host[0],
        [email],
        html_message=html_content,
        connection=connection
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
    
    mail_details = mail_conf()
    company_name = mail_details['company_name']
    company_mail = mail_details['company_mail']
    email_host = mail_details['email_host'][0]
    connection = get_email_connection(email_host = mail_details['email_host'][0], 
                                email_port = mail_details['email_port'][0],
                                email_host_user = mail_details['email_host_user'][0],
                                email_host_password = mail_details['email_host_password'][0],
                                email_tls= mail_details['email_tls'])
    
    print(f"WELCOME MAIL STATUS:{mail_details.get('welcome_mail')}")
    if not welcome_email:
        print(f"WELCOME MAIL IS TURNED OF, WILL NOT SENT MAIL TO THE NEW USER")
    else:
        email_otp_template = EmailTemplate.objects.filter(type='register').first()

        subject = email_otp_template.subject.replace("{{company_name}}", company_name)
        print(f"EMAIL USERNAME:{username}")
        # Replace placeholders in the subject


        # Replace placeholders in the HTML template
        html_content = email_otp_template.content.replace("{{username}}", username).replace("{{company_name}}", f"{company_name}").replace("{{support_email}}", f"{company_mail}")
        # html_content = html_content.replace("{{company_name}}", "Dating App")
        # html_content = content.replace("{{otp}}", otp)

        # Send email with both plain text and HTML content
        email_from = settings.EMAIL_HOST

        try:
            print(f"EMAIL HOST:{email_host}")
            send_mail(
                subject="Welcome",
                message="Welcome message body",
                from_email=email_host[0],
                recipient_list=[email],
                html_message=html_content,
                connection=connection,
            )
            result = "Email sent successfully."
        except BadHeaderError:
            result = "Invalid header found in the email."
            
        except Exception as e:
            result = f"An error occurred: {str(e)}"
        finally:
            print(f"EMAIL RESULT:{result}")
   
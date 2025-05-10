from django.db import migrations
from accounts.models import EmailTemplate
def seed_packages(apps, schema_editor):

    # Seed initial values
    welcome_email_content = """<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Welcome to {{company_name}} </title></head><body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; color: #333;"><div style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);"><h1 style="color: #333;">Welcome to {{company_name}}!</h1><p>Dear {{username}}, 💑</p><p>Congratulations! You've successfully created an account on {{company_name}}. We're delighted to have you join our community of like-minded individuals looking for meaningful connections.</p><p>Here are a few steps to get started:</p><ol><li>Complete your profile with accurate information and a profile picture. 📸</li><li>Set your partner preferences to help us match you with compatible individuals. ❤️🔍</li><li>Explore the app to discover potential matches in your area. 🌐</li><li>Start connecting and chatting with interesting people. 💬</li></ol><p>We're committed to providing a safe and enjoyable dating experience. If you have any questions or need assistance, feel free to reach out to our support team at {{support_email}}.</p><p>Thank you for choosing {{company_name}. We wish you a fantastic journey filled with exciting connections and meaningful relationships!</p><p>Best regards, {{company_name}}<br>{{support_email}}</p></div></body></html>"""
    otp_verification_email_content = """<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>OTP Verification for Dating App</title></head><body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; color: #333;"><div style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);"><h1 style="color: #333;">Hello {{username}}</h1><p>Enter this code <strong> {{otp}} </strong> in the login section of the Dating app to securely access your account.</p><p>If you didn't initiate this login attempt, please contact our support team immediately at <a href="mailto:dating@gmail.com">dating@gmail.com</a>.</p><p>Thank you for using our Dating App. We're here to help you find meaningful connections!</p><p>Best regards,<be>{{company_name}}<br>{{support_email}}</p></div></body></html>"""
    reset_password = """<p>Password Reset</p><h2>Password Reset 💖</h2><p>Dear <strong>{{username}}</strong> 👋,</p><p>🔒 Click the link below to reset your password:</p><p>🔑 Reset Password</p><p>Best regards, 💕 </p><p>{{company_name}} 💑 </p>"""
    
    EmailTemplate.objects.create(subject='Welcome to {{company_name}}', content=welcome_email_content, type='register')
    EmailTemplate.objects.create(subject='Your account verification email', content=otp_verification_email_content, type='otp')
    EmailTemplate.objects.create(subject="Reset Password", content = reset_password, type = "reset_password")
    
class Migration(migrations.Migration):

    dependencies = [
      ('accounts', '0061_emailtemplate_delete_welcomemessage'),  # Include the correct previous migration
    ]

    operations = [

        migrations.RunPython(seed_packages),  # Add this line to run the Python code
    ]
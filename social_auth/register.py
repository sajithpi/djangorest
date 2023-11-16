from rest_framework.exceptions import AuthenticationFailed
import random
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from accounts.models import User
from django.contrib.auth import authenticate as django_authenticate

def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)
def authenticate(email,password):
    try:
        user = User.objects.get(email=email)
        print(f"email:{email}, password:{password}")
    except User.DoesNotExist:
        print(f"user does't exists, email:{email}")
        return None
    if user.check_password(password):
        refresh = RefreshToken.for_user(user)

        return {
                'refresh_token':str(refresh),
                'access_token':str(refresh.access_token)
                }
    else:
        return None  # Incorrect password

def authenticate_for_android(name,password):
    try:
        user = User.objects.get(username=name)
        print(f"email:{name}, password:{password}")
    except User.DoesNotExist:
        print(f"user does't exists, name:{name}")
        return None
    if user.check_password(password):
        refresh = RefreshToken.for_user(user)

        return {
                'refresh_token':str(refresh),
                'access_token':str(refresh.access_token)
                }
    else:
        return None  # 


SOCIAL_SECRET = 'asdasd'
def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user_token = authenticate(email=email, password=SOCIAL_SECRET)
            print(f"registered_user_token:{registered_user_token}")
            return {
                
                'refresh_token':str(registered_user_token.get('refresh_token')),
                'access_token':str(registered_user_token.get('access_token'))
            }
        else:
            raise AuthenticationFailed(detail='Please continue your login using' + filtered_user_by_email[0].auth_provider)
    else:
        user = {
             'username':generate_username(name),
              'email':email,
             'password':SOCIAL_SECRET
        }    
        user = User.objects.create(
            username=generate_username(name),
            email=email,
        )
    
        # Set the user's password using set_password
        user.set_password(SOCIAL_SECRET)

        user.is_active = True
        user.auth_provider = provider
        user.save()

        new_user_token = authenticate(email=email, password = SOCIAL_SECRET)
        print(f"new user token:{new_user_token}")
        return {
            'email':email,
            # 'username':new_user.user_id,
            'refresh_token':str(new_user_token.get('refresh_token')),
            'access_token':str(new_user_token.get('access_token'))
            
        }
        
def register_social_user_for_android(provider, user_id, name):
    filtered_user_by_username = User.objects.filter(username=name)
    if filtered_user_by_username.exists():
        if provider == filtered_user_by_username[0].auth_provider:
            registered_user_token = authenticate(name=name, password=SOCIAL_SECRET)
            print(f"registered_user_token:{registered_user_token}")
            return {
                
                'refresh_token':str(registered_user_token.get('refresh_token')),
                'access_token':str(registered_user_token.get('access_token'))
            }
        else:
            raise AuthenticationFailed(detail='Please continue your login using' + filtered_user_by_username[0].auth_provider)
    else:
        user = {
             'username':generate_username(name),
             'password':SOCIAL_SECRET
        }    
        user = User.objects.create(
            username=generate_username(name),
        )
    
        # Set the user's password using set_password
        user.set_password(SOCIAL_SECRET)

        user.is_active = True
        user.auth_provider = provider
        user.save()

        new_user_token = authenticate(email=email, password = SOCIAL_SECRET)
        print(f"new user token:{new_user_token}")
        return {
            'email':email,
            # 'username':new_user.user_id,
            'refresh_token':str(new_user_token.get('refresh_token')),
            'access_token':str(new_user_token.get('access_token'))
            
        }
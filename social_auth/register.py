from rest_framework.exceptions import AuthenticationFailed
import random
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from accounts.models import User, UserProfile
from django.contrib.auth import authenticate as django_authenticate
from django.conf import settings

def generate_username(name):

    username = "".join(name.split(' ')).lower()
    return username
    # if not User.objects.filter(username=username).exists():
    #     return username
    # else:
    #     random_username = username + str(random.randint(0, 1000))
    #     return generate_username(random_username)
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


def check_profile_complete_status(email, type = 'web'):
    count = 0
    print(f"email:{email}")
    if type == 'web':
        user = User.objects.get(email = email)
    else:
        user = User.objects.get(username = email)
    user_profile = UserProfile.objects.get(user = user)
    if not user.gender or not user.email or not user.orientation or not user.date_of_birth or not user.interests.count():
        return 0
    return 1

    # if not user_profile.workout:
    #     count +=1
    # if not user_profile.family_plan:
    #     count +=1
    # if not user_profile.drink:
    #     count +=1
    # if not user_profile.religion:
    #     count +=1
    # if not user_profile.education:
    #     count +=1
    # if not user_profile.smoke:
    #     count +=1
    # if not user_profile.languages:
    #     count +=1
    return count

SOCIAL_SECRET = settings.SOCIAL_AUTH_PASSWORD
def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            # registered_user_token = authenticate(email=email, password=SOCIAL_SECRET)
            refresh_token = RefreshToken.for_user(filtered_user_by_email)
            access_token = str(refresh_token.access_token)
            profile_status = check_profile_complete_status(email=email)
            return {
                
                'refresh_token':str(refresh_token),
                'access_token':str(access_token),
                # 'is_admin':filtered_user_by_email[0].is_admin,
                'preference_status':profile_status
            }
        else:
            raise AuthenticationFailed(detail='Please continue your login using' + filtered_user_by_email[0].auth_provider)
    else:
        # user = {
        #      'username':generate_username(name),
        #       'email':email,
        #      'password':SOCIAL_SECRET
        # }    
        user = User.objects.create(
            username=generate_username(name),
            email=email,
        )
    
        # Set the user's password using set_password
        user.set_password(SOCIAL_SECRET)

        user.is_active = True
        user.auth_provider = provider
        user.save()

        # new_user_token = authenticate(email=email, password = SOCIAL_SECRET)
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        return {
            'email':email,
            # 'username':new_user.user_id,
            'refresh_token':str(refresh_token),
            'access_token':str(access_token),
            'is_admin':False,
            'preference_status':0,
            
        }
        
def register_social_user_for_android(provider, user_id, name):
    username=generate_username(name)
    filtered_user_by_username = User.objects.filter(username=username)
    if filtered_user_by_username.exists():
        if provider == filtered_user_by_username[0].auth_provider:
            # registered_user_token = authenticate_for_android(name=username, password=SOCIAL_SECRET)
            
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            
            
            profile_status = check_profile_complete_status(email=username, type = 'android')
            return {
                'profile_status' : profile_status,
                'refresh_token':str(refresh_token),
                'access_token':str(access_token)
            }
        else:
            raise AuthenticationFailed(detail='Please continue your login using' + filtered_user_by_username[0].auth_provider)
    else:
        # user = {
        #      'username':generate_username(name),
        #      'password':SOCIAL_SECRET
        # }    
        user = User.objects.create(
             username=username,
        )
    
        # Set the user's password using set_password
        user.set_password(SOCIAL_SECRET)

        user.is_active = True
        user.auth_provider = provider
        user.save()

        new_user_token = authenticate_for_android(username=username, password = SOCIAL_SECRET)
        print(f"new user token:{new_user_token}")
        return {
            'username':username,
            # 'username':new_user.user_id,
            'refresh_token':str(new_user_token.get('refresh_token')),
            'access_token':str(new_user_token.get('access_token'))
            
        }
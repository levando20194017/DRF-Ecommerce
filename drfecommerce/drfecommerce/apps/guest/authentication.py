import jwt
from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
import os
from dotenv import load_dotenv
from .models import Guest

# Load environment variables from .env file
load_dotenv()

class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class SafeJWTAuthentication(BaseAuthentication):
    '''
        custom authentication class for DRF and JWT
        https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py
    '''

    def authenticate(self, request):

        # User = get_user_model()
        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        try:
            # header = 'Token xxxxxxxxxxxxxxxxxxxxxxxx'
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, os.getenv('SECRET_KEY'), algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')

        user = Guest.objects.filter(id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_verified:
            raise exceptions.AuthenticationFailed('user is inactive')

        self.enforce_csrf(request)
        return (user, None)

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation
        """
        # check = CSRFCheck()
        # # populates request.META['CSRF_COOKIE'], which is used in process_view()
        # check.process_request(request)
        # reason = check.process_view(request, None, (), {})
        # print(reason)
        # if reason:
        #     # CSRF failed, bail with explicit error message
        #     raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
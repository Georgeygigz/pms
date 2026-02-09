from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from rest_framework import exceptions

from app.api.authentication.models import User



class JWTAuthentication(authentication.BaseAuthentication):
    """
    This is called on every request to check if the user is authenticated
    """

    @classmethod
    def authenticate(self, request):
        """
        This checks that the passed JWT token is valid and returns
        a user and his/her token on successful verification
        """

        # Get the passed token
        auth_header = authentication.get_authorization_header(
            request).decode('utf-8')
        if not auth_header or auth_header.split()[0].lower() != 'bearer':
            return None
        token = auth_header.split(" ")[1]
        # Attempt decoding the token
        
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms="HS256", )
            user = User.objects.get(email=payload['email'])
        except Exception as error:
            exception_mapper = {
                jwt.ExpiredSignatureError: 'Token expired. Please login to get a new token.',
                jwt.DecodeError: 'Authorization failed due to an Invalid token.',
                jwt.InvalidIssuerError: 'Cannot verify the token provided as the expected issuer does not match.',
                User.DoesNotExist: "No user found for token provided"
            }
            message = exception_mapper.get(
                type(error), 'Authorization failed.')
            raise exceptions.AuthenticationFailed(message)
        return (user, token)


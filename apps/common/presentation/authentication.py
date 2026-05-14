from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyUser:
    is_authenticated = True

class StaticAPIKeyAuthentication(BaseAuthentication):
    """
    Adaptador de entrada para validar la API Key en los headers HTTP.
    """
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None

        if api_key != settings.API_SECRET_KEY:
            raise AuthenticationFailed('API Key invalida o revocada.')

        return (APIKeyUser(), api_key)

    def authenticate_header(self, request):
        # Al definir esta cabecera, DRF sabe que debe retornar un HTTP 401
        return 'Api-Key'

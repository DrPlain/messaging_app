from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer
from rest_framework.response import Response
from rest_framework.validators import ValidationError


def get_token_pair(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)}

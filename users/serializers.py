from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from typing import Dict, Any, OrderedDict

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'referral_code', 'referred_by')
        extra_kwargs = {
            'id': {'read_only': True},
            'referral_code': {'read_only': True}
        }
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        # Remove password2 as it's only used for validation
        validated_data.pop('password2', None)
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that adds user info to the token.
    """
    @classmethod
    def get_token(cls, user: User) -> Dict[str, Any]:
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token

class GoogleLoginSerializer(SocialLoginSerializer):
    """
    Serializer for Google OAuth2 authentication.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "postmessage"  # Used by Google OAuth
    client_class = OAuth2Client

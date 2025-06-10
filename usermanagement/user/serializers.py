from rest_framework import serializers
from .models import User, Contact
from django.contrib.auth import authenticate


# userserialzer to convert the data from one object to another object (python object to json and vice versa)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `User` instance, with the password hashed.
        """
        user = User.objects.create_user( # Use create_user for proper password hashing
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''), # Use .get() for optional fields
            last_name=validated_data.get('last_name', '')
        )
        return user
    
# Contactserialzer to convert the data from one object to another object (python object to json and vice versa)
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
from rest_framework import serializers
#from apps.users.models import User
from django.contrib.auth.models import User

class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    """
    def create(self,validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self,instance,validated_data):
        updated_user = super().update(instance,validated_data)
        updated_user.set_password(validated_data['password'])
        updated_user.save()
        return updated_user
    """

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

    def to_representation(self,instance):
        return {
            'id': instance['id'],
            'username': instance['username'],
            'email': instance['email'],
            'password': instance['password']
        }


from rest_framework.schemas import AutoSchema
import coreapi
class CustomLoginSchema(AutoSchema):

    def get_serializer_fields(self, path, method):
        if method == 'POST':
            extra_fields = [
                coreapi.Field('username',
                              required=True,
                              location="formData",
                              type="string"
                              ),
                coreapi.Field('password',
                              required=True,
                              location="formData",
                              type="string"
                              ),
            ]
        else:
            extra_fields = []
        serializer_fields = super().get_serializer_fields(path, method)
        return serializer_fields + extra_fields        
from django.db.models import F
from django.http import Http404
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from profiles.models import CustomUser, EmailReset, Group, Organization, PasswordReminder, PasswordReminderQuestions


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug']


class CustomUserSerializer(serializers.ModelSerializer):
    registration_date = serializers.DateField(read_only=True, format='%Y/%m/%d', allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'katakana_name', 'hiragana_name', 'organization', 'is_active', 'bio',
                  'avatar', 'group_name', 'group_id', 'is_staff', 'last_login', 'login_counter',
                  'group_names', 'group_ids', 'email', 'first_name', 'last_name', 'registration_date']

    def validate_bio(self, value):
        if value:
            return value.replace('\n', ' ').replace('\r', ' ')
        else:
            return value


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['bio', 'avatar']


class RicAuthTokenObtainResponseSerializer(serializers.Serializer):
    """Serializer for the JWT token auth response

    Define the response so that OpenAPI tool chain can generate client code correctly
    """
    access = serializers.CharField(read_only=True, help_text="The Access token client code can use to access resources")
    refresh = serializers.CharField(
        read_only=True, help_text="The Refresh token that client code can use to get new JWT pair")


class RicAuthTokenUpdateCounterSerializer(TokenObtainPairSerializer):
    """Serializer for the JWT token auth response

    This Serializer will authenticate the user credentail and if credential are proper then it will
     update the login_counter for the user.

    It will return refresh token and access token as part of response.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        CustomUser.objects.filter(username=self.user.username).update(login_counter=F('login_counter') + 1)
        return data


class PasswordReminderQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReminderQuestions
        fields = ['id', 'organization', 'question']


class PasswordReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReminder
        fields = ['id', 'user', 'question', 'answer']


class SubGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'hierarchy', 'sub_groups_count', 'users_count']


class GroupSerializer(serializers.ModelSerializer):
    sub_groups = SubGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'hierarchy', 'organization',
                  'sub_groups_count', 'users_count', 'parent_group', 'sub_groups']


class RandomUserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'avatar']

    @extend_schema_field(OpenApiTypes.STR)
    def get_avatar(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.avatar.url)


class RandomUserAvatarListSerializer(serializers.ListSerializer):
    child = RandomUserAvatarSerializer()


class EmailResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailReset
        fields = ['email', 'auth_code']


class EmailResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailReset
        fields = ['id', 'user', 'email', 'auth_code', 'uuid']

    def validate(self, data):
        user = self.context.get("request", {}).user
        if user is None:
            raise Http404()

        user_email = CustomUser.objects.filter(email=data["email"])
        if user_email:
            raise serializers.ValidationError(_("This email is already taken."))

        return data

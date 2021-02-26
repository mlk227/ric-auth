import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

import django_filters
import rest_framework
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from base.filters import DynamicSearchFilter
from base.permissions import IsOptionsOrAuthenticated
from profiles.filters import CustomUserFilterSet, GroupFilterSet
from profiles.models import (
    CustomUser, EmailReset, Group, Organization, PasswordReminder, PasswordReminderQuestions, UserGroupRole)
from profiles.serializers import (
    CustomUserSerializer, CustomUserUpdateSerializer, EmailResetRequestSerializer, EmailResetSerializer,
    GroupSerializer, OrganizationSerializer, PasswordReminderQuestionsSerializer, PasswordReminderSerializer,
    RandomUserAvatarListSerializer, RandomUserAvatarSerializer, RicAuthTokenObtainResponseSerializer,
    RicAuthTokenUpdateCounterSerializer)


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API endpoint that allows anonymous reading of organization names.
    '''
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filterset_fields = ['slug', ]


@extend_schema(
    request=CustomUserUpdateSerializer,
)
class CustomUserViewSet(viewsets.ModelViewSet):
    """API to return user details.

    Possible ordering fields are `username` and `id`.
    Possible filtering fields are documented below.
    Searching will search the katakana_name, hiragana_name, and ID.

    For GET and PATCH API calls, pass in id `0` for the current logged in user.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    ordering_fields = ['username', 'id']
    search_fields = ['katakana_name', 'hiragana_name', 'id']
    filterset_class = CustomUserFilterSet
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        rest_framework.filters.OrderingFilter,
        DynamicSearchFilter,
    ]
    http_method_names = ['get', 'patch', 'options']
    parser_classes = [MultiPartParser, ]
    search_patterns = {
        'user_info': ['katakana_name', 'hiragana_name', 'id'],
        'user_and_group_info': ['katakana_name', 'hiragana_name', 'id', 'group_roles__group__name',
                                'group_roles__group__code'],
    }

    def get_object(self):
        user_id = self.kwargs["pk"]
        if self.request.user.is_authenticated and user_id == "0":
            obj = self.request.user
        else:
            obj = get_object_or_404(self.get_queryset(), pk=user_id)

        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(
    request=TokenObtainPairSerializer,
    responses=RicAuthTokenObtainResponseSerializer,
)
class RicAuthTokenObtainPairView(TokenObtainPairView):
    """Takes a set of user credentials and returns an access/refresh JWT pair.

    The input username/password in Json is straightforward. For now they are checked against the fields in `CustomUser`
    model. Later on with Benefit One Platform Integration we'll send the creds to BOF for verifying.

    The response is an access/refresh JWT token pair. Client wil use the access token to access various resources. The
    access token is set to expire quickly (currently 1 hour) for security reason. If the user is still active, client
    will use the refresh token to call the `refresh` API, and get a new pair of tokens. So it's transparent to the user:
    As long as they are active, they are always logged in. Once they become inactive, the tokens will timeout and the
    user will need to login again.
    """
    serializer_class = RicAuthTokenUpdateCounterSerializer


@extend_schema(
    request=TokenRefreshSerializer,
    responses=RicAuthTokenObtainResponseSerializer,
)
class RicAuthTokenRefreshView(TokenRefreshView):
    """Takes a refresh JWT and returns an access/refresh JWT pair if the refresh token is valid.

    Details are in the `/api/token/` API doc.
    """
    pass


class PasswordReminderQuestionsViewSet(viewsets.ReadOnlyModelViewSet):
    """API ednpoint that allows password reminder questions."""

    queryset = PasswordReminderQuestions.objects.all()
    serializer_class = PasswordReminderQuestionsSerializer
    permission_classes = [IsOptionsOrAuthenticated, ]

    def get_queryset(self):
        organization = self.request.user.organization
        queryset = self.queryset.filter(organization=organization)
        if not queryset:
            queryset = self.queryset.filter(organization=None)
        return queryset


class PasswordReminderViewSet(viewsets.ModelViewSet):
    """API ednpoint that allows password reminder"""

    queryset = PasswordReminder.objects.all()
    serializer_class = PasswordReminderSerializer
    permission_classes = [IsOptionsOrAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset which allowed reading of Groups.
    Possible ordering fields are `name`, 'code` and `id`.
    Possible filtering fields are documented `organization`.
    Searching will search the name, code.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    ordering_fields = ['name', 'id', 'code']
    search_fields = ['name', 'code']
    filter_backends = [
        rest_framework.filters.OrderingFilter, rest_framework.filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
    ]
    filterset_class = GroupFilterSet


@extend_schema(
    responses=RandomUserAvatarListSerializer,
)
class RandomUserAvatarViewSet(ListAPIView):
    """
    API endpoint that allows logged in user to give avatar of their group's users.
    """
    pagination_class = None

    def get(self, request, *args, **kwargs):
        user = self.request.user
        groups = UserGroupRole.objects.filter(user=user).values_list("group", flat=True).distinct()
        users = UserGroupRole.objects.filter(group__in=groups).values_list("user", flat=True).distinct()
        final_users = users.exclude(user=user)[0:6]
        random_users = CustomUser.objects.filter(id__in=final_users)

        serializer = RandomUserAvatarSerializer(random_users, many=True, context={"request": request})
        return Response(serializer.data)


class EmailResetViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows to change email.
    """
    queryset = EmailReset.objects.all()
    serializer_class = EmailResetSerializer

    @extend_schema(
        request=EmailResetRequestSerializer,
    )
    def create(self, request):
        """
        API endpoint that allows to change email.
        """
        user = request.user
        email = request.data.get("email")
        auth_code = request.data.get("auth_code")
        uuid_str = str(uuid.uuid4())

        data = {
            "user": user.id,
            "email": email,
            "auth_code": auth_code,
            "uuid": uuid_str,
        }

        serializer = EmailResetSerializer(data=data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        verification_page_url = settings.FE_BASE_URL + "/my-page/identity-verification/?uuid=" + uuid_str
        content = f"URL Link : {verification_page_url}"

        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=email,
                subject="Verification mail for email change",
                html_content=content
            )

            sg = SendGridAPIClient(settings.SG_API_KEY)
            sg.send(message)

        except Exception as e:
            return Response(str(e), HTTP_400_BAD_REQUEST)

        return Response(serializer.data, HTTP_201_CREATED)

    @action(detail=False, methods=['PATCH'])
    def verification(self, request):
        """
        API endpoint that allows to verify email change.
        """
        user = request.user
        email = request.data.get("email")
        auth_code = request.data.get("auth_code")
        uuid = request.data.get("uuid")

        email_reset = get_object_or_404(EmailReset, user=user, email=email, uuid=uuid, is_deleted=False)

        if auth_code != email_reset.auth_code:
            email_reset.fail_attempt += 1
            email_reset.save()

            if email_reset.fail_attempt == settings.EMAIL_RESET_ATTEMPT_LIMIT:
                email_reset.delete()
                return Response({_("You have reached the maximum attempt limit.")}, HTTP_400_BAD_REQUEST)

            return Response({_("Invalid auth code.")}, HTTP_400_BAD_REQUEST)

        user.email = email
        user.save()
        email_reset.delete()
        return Response("Email changed successfully.", HTTP_200_OK)

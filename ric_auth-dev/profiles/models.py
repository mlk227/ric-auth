import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from base.models import CreatedUpdatedSoftDeleteMixin, SoftDeleteMixin
from profiles.helpers import static_image_path_for_avatar
from profiles.signals import auto_delete_file_on_change


class Organization(CreatedUpdatedSoftDeleteMixin):
    "One organization is a client company"
    name = models.CharField(max_length=100, help_text="name of the organization/company")
    slug = models.SlugField(
        max_length=100, help_text="a unique, URL ready name of the organization name", editable=False, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            new_slug = slugify(self.name)
            if Organization.objects.filter(slug=new_slug).exists():
                new_slug += str(datetime.date.today().toordinal())
            self.slug = new_slug
        super(Organization, self).save()


class Group(CreatedUpdatedSoftDeleteMixin):
    name = models.CharField(max_length=100, help_text="name of the group")
    code = models.CharField(max_length=100, help_text="companies usually have a code for the group")
    hierarchy = models.PositiveSmallIntegerField(
        help_text="which level the group is in. With the top level group being 1. For easy reference only, should be "
        "calculated from parent_group")
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT,
                                     related_name="groups", help_text="which organization this group belongs to")
    parent_group = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, related_name="sub_groups",
                                     null=True, help_text="The parent group. None if this is the top level group")

    def __str__(self):
        return self.name

    @property
    @extend_schema_field(OpenApiTypes.INT)
    def sub_groups_count(self):
        return self.sub_groups.count()

    @property
    @extend_schema_field(OpenApiTypes.INT)
    def users_count(self):
        """Number of users in a group."""
        return len([user for user in CustomUser.objects.iterator() if self.id in user.group_ids])


class CustomUser(AbstractUser, CreatedUpdatedSoftDeleteMixin):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="users",
                                     help_text="Which organization (client company) the user belongs to.")
    katakana_name = models.CharField(max_length=128, help_text="Katakana name in Japanese")
    hiragana_name = models.CharField(max_length=128, help_text="Hiragana name in Japanese")
    bio = models.TextField(null=True, help_text="A short description of the user, provided by the user themselves")
    avatar = models.ImageField(
        upload_to=static_image_path_for_avatar,
        help_text="User avatar. Response will be full URL",
        null=True,
    )
    login_counter = models.IntegerField(help_text="Number of times user has logged in.", default=0)
    registration_date = models.DateField(null=True, help_text="Service registration date of the user")

    REQUIRED_FIELDS = ['organization']

    @property
    def all_groups(self):
        """Return all the groups the user belong to in a queryset."""
        return Group.objects.filter(pk__in=UserGroupRole.objects.filter(user=self).values_list('group', flat=True))

    @property
    def group_names(self):
        """Return the name of all the groups the user belong to in a list."""
        return [x.name for x in self.all_groups.all()]

    @property
    def group_name(self):
        """Return the name of the first group the user belongs to.

        Being backward compatible.

        Note one user can belong to multiple groups and this will return a random one among them.
        """
        return self.all_groups.first().name

    @property
    def group_ids(self):
        """Return the ID of all the groups the user belong to in a list."""
        return [x.id for x in self.all_groups.all()]

    @property
    def group_id(self):
        """Return the name of the first group the user belongs to.

        Being backward compatible.

        Note one user can belong to multiple groups and this will return a random one among them.
        """
        return self.all_groups.first().id

    def __str__(self):
        return self.hiragana_name


models.signals.pre_save.connect(auto_delete_file_on_change, sender=CustomUser)


class Role(CreatedUpdatedSoftDeleteMixin):
    class RoleType(models.IntegerChoices):
        default_normal_user = 0, _("default normal user")
        normal_user = 1, _("normal user")
        admin_user = 2, _("admin user")

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)

    name = models.CharField(max_length=100)
    role_type = models.PositiveSmallIntegerField(choices=RoleType.choices)

    class Meta:
        indexes = [
            models.Index(fields=['organization'])
        ]

    def __str__(self):
        return "{} for org ID {}".format(self.name, self.organization)


class RolePermission(CreatedUpdatedSoftDeleteMixin):
    class PermissionType(models.IntegerChoices):
        read_overal_result = 11112, _("read overal result")
        read_user_registration_info = 21222, _("read user registration info")
        edit_user_registration_info = 21223, _("edit user registration info")

    permission = models.PositiveIntegerField(choices=PermissionType.choices)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    allow = models.BooleanField(default=True)


class UserGroupRole(CreatedUpdatedSoftDeleteMixin):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="group_roles")
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_groups")

    class Meta:
        unique_together = ('user', 'group', 'role')
        indexes = [
            models.Index(fields=['group'])
        ]


class PasswordHistory(CreatedUpdatedSoftDeleteMixin):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="password_history")
    password_hash = models.CharField(max_length=128, blank=True, null=False)


class PasswordReminderQuestions(CreatedUpdatedSoftDeleteMixin):
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.DO_NOTHING,
        help_text="If not set, it'll be used by all clients with 'custom password reminder questions' feature disabled")
    question = models.TextField()


class PasswordReminder(CreatedUpdatedSoftDeleteMixin):
    """Password reminder questions and answers.

    So that user can reset password on their own.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="password_reminder")
    question = models.ForeignKey(PasswordReminderQuestions, on_delete=models.PROTECT)
    answer = models.CharField(max_length=128)


class PasswordResetRequest(SoftDeleteMixin):
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128)
    birthday = models.DateField()
    message = models.TextField()


class PasswordResetResponse(CreatedUpdatedSoftDeleteMixin):
    request = models.ForeignKey(PasswordResetRequest, on_delete=models.PROTECT, related_name="response")
    password_reset = models.BooleanField(default=False)


class EmailReset(CreatedUpdatedSoftDeleteMixin):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="email_reset")
    email = models.EmailField(max_length=128)
    auth_code = models.CharField(max_length=4)
    uuid = models.CharField(max_length=36)
    fail_attempt = models.PositiveSmallIntegerField(default=0)

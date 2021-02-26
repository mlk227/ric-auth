import os

from django.utils.timezone import now


def _static_user_image_path(instance, filename, static_file_name):
    """Generate static file name for user.

    Instance has to be an CustomUser object.
    """
    from profiles.models import CustomUser
    assert isinstance(instance, CustomUser)

    current_time = now()
    return "user_avatars/{}/{}_{}{}".format(
        current_time.strftime("%Y/%m/%d"),
        instance.pk,
        static_file_name,
        os.path.splitext(filename)[-1]
    )


def static_image_path_for_avatar(instance, filename):
    return _static_user_image_path(instance, filename, "avatar")

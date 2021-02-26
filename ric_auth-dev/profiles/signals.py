import os


def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_avatar = sender.objects.get(pk=instance.pk).avatar
    except sender.DoesNotExist:
        return False

    new_avatar = instance.avatar

    if old_avatar and new_avatar and not old_avatar == new_avatar:
        if os.path.isfile(old_avatar.path):
            os.remove(old_avatar.path)

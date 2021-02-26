#!/usr/bin/env bash -e

INCLUDED_MODELS="
    profiles.Organization
    profiles.CustomUser
    profiles.Group
    profiles.Role
    profiles.UserGroupRole
    profiles.PasswordReminderQuestions
    profiles.PasswordReminder
"

python manage.py dumpdata --indent 4 ${INCLUDED_MODELS}  > docker/test/fixtures/fixtures.json

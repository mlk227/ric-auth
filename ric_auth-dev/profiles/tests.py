import datetime
import json

from freezegun import freeze_time
from rest_framework import status

from base.tests import AuthBaseTests, AuthorizedTestSetup
from profiles.models import CustomUser, Group, Organization, PasswordReminderQuestions


class CreateOrganizationTest(AuthBaseTests):
    "Test organization can be created correctly from Django."

    def test_create_org(self):
        org = Organization.objects.create(name="abc")
        self.assertEqual(org.slug, "abc")

    def test_org_with_non_ascii_name(self):
        org = Organization.objects.create(name="会社コード")
        self.assertEqual(org.slug, "")

    @freeze_time("2020-09-01")
    def test_duplicate_org_name(self):
        org_name = "会社コード"
        org = Organization.objects.create(name=org_name)
        self.assertEqual(org.slug, "")
        org = Organization.objects.create(name=org_name)
        self.assertEqual(org.slug, "737669")


class GetCustomUsersTest(AuthorizedTestSetup):
    def setUp(self):
        super().setUp()

    def test_get_users_list(self):
        users = CustomUser.objects.all()
        response = self.client.get("/api/CustomUser/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], users.count())

    def test_get_users_list_excluding_current_user(self):
        users = CustomUser.objects.all()
        response = self.client.get("/api/CustomUser/", data={"exclude_current_user": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], (users.count() - 1))

    def test_get_users_list_including_current_user(self):
        users = CustomUser.objects.all()
        response = self.client.get("/api/CustomUser/", data={"exclude_current_user": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], users.count())

    def test_get_users_list_with_random_parameter(self):
        users = CustomUser.objects.all()
        response = self.client.get("/api/CustomUser/", data={"exclude_current_user": "abc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], users.count())

    def test_get_user_list_with_name(self):
        response = self.client.get("/api/CustomUser/", data={"katakana_name": "dev"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 3)

    def test_get_user_list_with_combined_name_and_org(self):
        response = self.client.get("/api/CustomUser/", data={"katakana_name": "dev", "organization": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

    def test_get_individual_user(self):
        user = CustomUser.objects.get(id=1)
        response = self.client.get("/api/CustomUser/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('katakana_name'), user.katakana_name)
        self.assertSetEqual(set(response.data.get('group_ids')), set([1, 2]))
        self.assertSetEqual(set(response.data.get('group_names')),
                            set(["tech", "Group name 1"]))
        self.assertIn(response.data.get('group_id'), [1, 2])
        self.assertIn(response.data.get('group_name'), ["tech", "Group name 1"])

    def test_search_users_list_by_multiple_keyword(self):
        response = self.client.get("/api/CustomUser/", data={"search": "dev rewardz3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json().get('results')[0].get('hiragana_name'), 'rewardz3')

    def test_search_users_list_by_multiple_keyword_not_found(self):
        response = self.client.get("/api/CustomUser/", data={"search": "boj2 rewardz4"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_search_users_list_by_mixed_multiple_keyword_not_found(self):
        response = self.client.get("/api/CustomUser/", data={"search": "boj rewardz3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_search_users_list_user_id(self):
        response = self.client.get("/api/CustomUser/", data={"search": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['katakana_name'], 'boj-dev')

    def test_search_users_list_with_search_pattern(self):
        response = self.client.get("/api/CustomUser/", data={"search": "end", "search_pattern": "user_and_group_info"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)

    def test_search_users_list_with_non_exist_search_pattern(self):
        response = self.client.get("/api/CustomUser/", data={"search": "end", "search_pattern": "does_not_exist"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_user_not_found(self):
        response = self.client.patch(
            '/api/CustomUser/300/',
            json.dumps({
                "bio": "devi@rewardz.sg i bio",
                "avatar": None,
            }),
            follow=True,
            content_type='application/json',
        )

        self.assertEqual(response.data, {"detail": "Not found."})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_user_bio(self):
        response = self.client.patch(
            '/api/CustomUser/3/',
            {
                "bio": "devi@rewardz.sg i bio",
            },
            follow=True,
        )
        self.assertEqual(response.data["bio"], "devi@rewardz.sg i bio")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_user_avatar(self):
        with open("docker/test/icon-dummy.png", 'rb') as fp:
            response = self.client.patch(
                '/api/CustomUser/3/',
                {
                    "avatar": fp,
                },
                follow=True,
            )
            self.assertEqual(
                response.data["bio"], "I like to make new friends and like to discuss current affairs. "
                "I am very honest and sincere towards my work.")
            self.assertIn(datetime.date.today().strftime("%Y/%m/%d"), response.json()['avatar'])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_current_user(self):
        # this is the default logged in user
        user = CustomUser.objects.get(id=1)
        response = self.client.get("/api/CustomUser/0/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('katakana_name'), user.katakana_name)

    def test_can_not_get_current_user_without_logging_in(self):
        self.client.credentials()
        response = self.client.get("/api/CustomUser/0/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_users_list_with_group_ids(self):
        response = self.client.get("/api/CustomUser/", data={"group_ids": '2,3'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 2)
        self.assertTrue(any(id in response.json()['results'][0]['group_ids'] for id in [2, 3]))


class GetPasswordReminderQuestionsTest(AuthorizedTestSetup):
    def setUp(self):
        super().setUp()

    def test_get_password_reminder_questions_list(self):
        questions = PasswordReminderQuestions.objects.filter(organization=1)
        if not questions:
            questions = PasswordReminderQuestions.objects.filter(organization=None)
        response = self.client.get("/api/password_reminder_question/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], questions.count())

    def test_get_password_reminder_questions(self):
        response = self.client.get("/api/password_reminder_question/1/")
        question = "What is your favorite movie title?"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['question'], question)


class GetPasswordReminderTest(AuthorizedTestSetup):
    def setUp(self):
        super().setUp()

    def test_get_password_reminder(self):
        response = self.client.get("/api/password_reminder/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['answer'], "India")

    def test_patch_password_reminder(self):
        response = self.client.patch(
            '/api/password_reminder/1/',
            json.dumps({
                "question": 1,
                "answer": "Pirates of the caribbean",
            }),
            follow=True,
            content_type='application/json',
        )

        self.assertEqual(response.data["answer"], "Pirates of the caribbean")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserLoginCount(AuthorizedTestSetup):
    def setUp(self):
        super().setUp()

    def test_user_login_count_after_successful_login(self):
        response_before_login = self.client.get('/api/CustomUser/1/')
        response = self.client.post(
            '/api/token/',
            json.dumps({
                "username": 'dev@rewardz.sg',
                "password": "Pass1234",
            }),
            follow=True,
            content_type='application/json',
        )
        response_after_login = self.client.get('/api/CustomUser/1/')
        self.assertEqual(response_before_login.data["login_counter"], 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_after_login.data["login_counter"], 2)

    def test_user_login_count_after_unsuccessful_login(self):
        response_before_login = self.client.get('/api/CustomUser/1/')
        response = self.client.post(
            '/api/token/',
            json.dumps({
                "username": 'dev@rewardz.sg',
                "password": "tempPass",
            }),
            follow=True,
            content_type='application/json',
        )
        response_after_login = self.client.get('/api/CustomUser/1/')
        self.assertEqual(response_before_login.data["login_counter"], 1)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_after_login.data["login_counter"], 1)


class TestRandomUserAvatar(AuthorizedTestSetup):
    """ Test module for GET random user avatar API """

    def test_get_random_user_avatar(self):
        response = self.client.get('/api/random_user_avatar/')
        for user in response.json():
            if user["id"] == 2:
                avatar_2 = user["avatar"]

        self.assertTrue(avatar_2.endswith("/media/user_avatars/2020/10/15/avatar.png"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestEmailReset(AuthorizedTestSetup):
    """ Test module for EmailReset API """

    def test_patch_email_reset(self):
        post_response = self.client.post(
            '/api/email_reset/',
            json.dumps({
                "email": "test.rewardz@gmail.com",
                "auth_code": "1920",
            }),
            follow=True,
            content_type='application/json',
        )

        response = self.client.patch(
            '/api/email_reset/verification/',
            json.dumps({
                "email": "test.rewardz@gmail.com",
                "auth_code": "1920",
                "uuid": post_response.data["uuid"],
            }),
            follow=True,
            content_type='application/json',
        )

        self.assertEqual(response.data, "Email changed successfully.")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetGroupTest(AuthorizedTestSetup):
    def setUp(self):
        super().setUp()

    def test_get_group_list(self):
        groups = Group.objects.all()
        response = self.client.get("/api/group/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], groups.count())

    def test_filter_group_by_organization(self):
        groups = Group.objects.filter(organization=2)
        response = self.client.get("/api/group/", data={"organization": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], groups.count())

    def test_filter_group_by_hierarchy(self):
        groups = Group.objects.filter(hierarchy=2)
        response = self.client.get("/api/group/", data={"hierarchy": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], groups.count())

    def test_filter_group_by_both_group_and_hierarchy(self):
        groups = Group.objects.filter(hierarchy=2, organization=2)
        response = self.client.get("/api/group/", data={"hierarchy": 2, "organization": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], groups.count())

    def test_sub_groups_are_included(self):
        response = self.client.get("/api/group/2/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['sub_groups_count'], 3)
        self.assertEqual(len(response.json()['sub_groups']), 3)

    def test_filter_group_by_ids(self):
        groups = Group.objects.filter(id__in=[1, 2])
        response = self.client.get("/api/group/", data={"ids": '1,2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], groups.count())

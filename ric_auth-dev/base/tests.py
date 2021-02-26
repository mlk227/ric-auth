from django.urls import reverse
import json
from rest_framework.test import APITestCase


class AuthBaseTests(APITestCase):
    fixtures = ['docker/test/fixtures/fixtures.json']


class AuthorizedTestSetup(AuthBaseTests):
    def setUp(self):
        auth_response = self.client.post(
            reverse('token_obtain_pair'),
            json.dumps({
                "username": "dev@rewardz.sg",
                "password": "Pass1234"
            }),
            content_type='application/json',
            follow=True
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + auth_response.data.get('access'))
        return super().setUp()

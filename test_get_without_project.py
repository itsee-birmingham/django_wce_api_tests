import json
from django.utils import timezone
from django.test import TestCase, Client
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.authtoken.models import Token
from unittest import skip
from api_tests import models
from collation import models as collation_models
from transcriptions import models as transcription_models


User = get_user_model()


class MyAPITestCase(TestCase):

    def add_user(self, credentials):
        user = User.objects.create_user(**credentials)
        user.save()
        return user

    def add_superuser(self, credentials):
        g1 = Group(name='api_tests_superusers')
        g1.save()
        user = User.objects.create_user(**credentials)
        user.groups.add(g1)
        user.save()
        return user

    def add_data(self):

        # add users
        self.u1 = self.add_user({'username': 'User1',
                                 'email': 'user1@example.com',
                                 'password': 'secret'})
        self.u2 = self.add_user({'username': 'User2',
                                 'email': 'user2@example.com',
                                 'password': 'secret'})
        self.u3 = self.add_superuser({'username': 'User3',
                                      'email': 'user3@example.com',
                                      'password': 'secret'})
        self.u4 = self.add_user({'username': 'User4',
                                 'email': 'user4@example.com',
                                 'password': 'secret'})

        e1_data = {'user': self.u1,
                   'active': True}
        self.e1 = models.Editor.objects.create(**e1_data)
        e2_data = {'user': self.u2,
                   'active': True}
        self.e2 = models.Editor.objects.create(**e2_data)
        e3_data = {'user': self.u3,
                   'active': True}
        self.e3 = models.Editor.objects.create(**e3_data)
        e4_data = {'user': self.u4,
                   'active': True}
        self.e4 = models.Editor.objects.create(**e4_data)

        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'active': True
                   }
        self.a1 = models.Author.objects.create(**a1_data)
        a2_data = {'identifier': 'JS2',
                   'name': 'Jane Smart',
                   'age': 34,
                   'active': True
                   }
        self.a2 = models.Author.objects.create(**a2_data)

        w1_data = {'identifier': 'W1',
                   'title': 'My First Book',
                   'author': self.a1
                   }
        self.w1 = models.Work.objects.create(**w1_data)

        w2_data = {'identifier': 'W2',
                   'title': 'My Second Book',
                   'author': self.a1
                   }
        self.w2 = models.Work.objects.create(**w2_data)

        w3_data = {'identifier': 'W3',
                   'title': 'My Best Book',
                   'author': self.a2
                   }
        self.w3 = models.Work.objects.create(**w3_data)

        w4_data = {'identifier': 'W4',
                   'title': 'Another Great Book',
                   'author': self.a2
                   }
        self.w4 = models.Work.objects.create(**w4_data)

        d1_data = {'work': self.w1,
                   'accept': True,
                   'summary_notes': 'accepted for publication',
                   'public': True,
                   'user': self.u4}
        self.d1 = models.Decision.objects.create(**d1_data)

        d2_data = {'work': self.w2,
                   'summary_notes': 'needs further cosideration',
                   'public': False,
                   'user': self.u4}
        self.d2 = models.Decision.objects.create(**d2_data)

        d3_data = {'work': self.w3,
                   'accept': True,
                   'summary_notes': 'third review requested',
                   'user': self.u2}
        self.d3 = models.Decision.objects.create(**d3_data)

        d4_data = {'work': self.w4,
                   'accept': False,
                   'summary_notes': 'Not ready yet',
                   'public': True,
                   'user': self.u2}
        self.d4 = models.Decision.objects.create(**d4_data)

        r1_data = {'notes': 'Good',
                   'score': 7,
                   'work': self.w1,
                   'user': self.u1
                   }
        self.r1 = models.Review.objects.create(**r1_data)

        r2_data = {'notes': 'Great',
                   'score': 10,
                   'work': self.w1,
                   'user': self.u2
                   }
        self.r2 = models.Review.objects.create(**r2_data)

        r3_data = {'notes': 'Good',
                   'score': 6,
                   'work': self.w2,
                   'user': self.u1
                   }
        self.r3 = models.Review.objects.create(**r3_data)

        r4_data = {'notes': 'not great',
                   'score': 3,
                   'work': self.w2,
                   'user': self.u3
                   }
        self.r4 = models.Review.objects.create(**r4_data)

        r5_data = {'notes': 'okay',
                   'score': 5,
                   'work': self.w2,
                   'user': self.u4
                   }
        self.r5 = models.Review.objects.create(**r5_data)

        r6_data = {'notes': 'Looking good',
                   'score': 8,
                   'work': self.w3,
                   'user': self.u4
                   }
        self.r6 = models.Review.objects.create(**r6_data)


class TestNoAvailabilitySetIsAssignedPrivate(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        models.Review.AVAILABILITY = None
        self.add_data()

    def tearDown(self):
        models.Review.AVAILABILITY = 'private'

    def test_availability_assignment_by_using_not_logged_in_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 401)

    def test_user_has_access(self):
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)

    def test_superuser_sees_all(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 6)


class TestInvalidAvailabilityAssignment(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        models.Review.AVAILABILITY = 'nonsense'
        self.add_data()

    def tearDown(self):
        models.Review.AVAILABILITY = 'private'

    def test_invalid_availability_assignment_by_using_not_logged_in_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model availability incompatible with API (code 10005)')


class APIItemListTestsLoggedInModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def test_get_list_returns_401_if_not_logged_in(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'editor'))
        self.assertEqual(response.status_code, 401)

    def test_get_list_returns_all_editors_if_logged_in(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'editor'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 4)


class APIItemDetailTestsLoggedInModels(MyAPITestCase):
    base_url = '/api/{}/{}/{}'

    def test_get_list_returns_401_if_not_logged_in(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'editor', self.e1.id))
        self.assertEqual(response.status_code, 401)

    def test_get_list_returns_all_editors_if_logged_in(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'editor', self.e2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['id'], self.e2.id)


class APIItemListTestsPublicModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def test_get_list_returns_json_200(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'author'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_list_returns_correct_data(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertEqual(response_json['results'][0]['identifier'], self.a1.identifier)
        self.assertEqual(response_json['results'][1]['identifier'], self.a2.identifier)

    def test_get_list_returns_correct_data_with_sort(self):
        self.add_data()
        response = self.client.get('%s?_sort=name' % self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertEqual(response_json['results'][0]['identifier'], self.a2.identifier)
        self.assertEqual(response_json['results'][1]['identifier'], self.a1.identifier)

    def test_get_list_returns_correct_data_with_field_filtering(self):
        self.add_data()
        response = self.client.get('%s?_fields=id,name' % self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertIn('name', response_json['results'][0])
        self.assertIn('id', response_json['results'][0])
        self.assertNotIn('identifier', response_json['results'][0])
        self.assertNotIn('active', response_json['results'][0])

    def test_get_list_returns_correct_data_with_pagination(self):
        self.add_data()
        response = self.client.get('%s?limit=1' % self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 1)

    def test_get_list_returns_correct_data_with_multiple_parameters(self):
        self.add_data()
        response = self.client.get('%s?age=28&name=*S*' % self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 1)

    def test_get_list_returns_correct_data_with_repeated_parameters(self):
        self.add_data()
        response = self.client.get('%s?age=<40&age=>30' % self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 1)


class APIItemDetailTestsPublicModels(MyAPITestCase):
    base_url = '/api/{}/{}/{}'

    def test_get_list_returns_json_200(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'author', self.a1.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_list_returns_correct_data(self):
        self.add_data()
        response = self.client.get(self.base_url.format('api_tests', 'author', self.a1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['id'], self.a1.id)
        self.assertEqual(response_json['name'], 'John Smith')


class APIItemListTestsPublicOrUserModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        self.add_data()

    def test_get_restricted_list_returns_all_public_for_anonymous_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertNotEqual(response_json['results'][0]['summary_notes'], response_json['results'][1]['summary_notes'])
        self.assertIn(response_json['results'][0]['summary_notes'], [self.d1.summary_notes, self.d4.summary_notes])
        self.assertIn(response_json['results'][1]['summary_notes'], [self.d1.summary_notes, self.d4.summary_notes])

    def test_get_restricted_list_returns_all_public_for_anonymous_user_with_sort(self):
        response = self.client.get('%s?_sort=work__id' % self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertEqual(response_json['results'][0]['summary_notes'], self.d1.summary_notes)
        self.assertEqual(response_json['results'][1]['summary_notes'], self.d4.summary_notes)

    def test_get_restricted_list_returns_all_public_for_anonymous_user_with_filters(self):
        response = self.client.get('%s?accept=true' % self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 1)
        self.assertEqual(len(response_json['results']), 1)
        self.assertEqual(response_json['results'][0]['summary_notes'], self.d1.summary_notes)

    def test_get_restricted_list_returns_nothing_for_anonymous_user_if_no_public_items(self):
        # now make the two public ones private
        self.d1.public = False
        self.d1.save()
        self.d4.public = False
        self.d4.save()
        response = self.client.get(self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 0)
        self.assertEqual(len(response_json['results']), 0)

    def test_get_restricted_list_returns_public_and_owned_for_logged_in_regular_user(self):
        client = APIClient()
        login = client.login(username='user4@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 3)
        self.assertEqual(len(response_json['results']), 3)
        self.assertNotEqual(response_json['results'][0]['summary_notes'], self.d3.summary_notes)
        self.assertNotEqual(response_json['results'][1]['summary_notes'], self.d3.summary_notes)
        self.assertNotEqual(response_json['results'][2]['summary_notes'], self.d3.summary_notes)

    def test_get_restricted_list_returns_public_only_for_logged_in_regular_user_if_not_owned(self):
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)
        self.assertIn(response_json['results'][0]['summary_notes'], [self.d1.summary_notes, self.d4.summary_notes])
        self.assertIn(response_json['results'][1]['summary_notes'], [self.d1.summary_notes, self.d4.summary_notes])

    def test_get_restricted_list_returns_all_for_app_superuser(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 4)
        self.assertEqual(len(response_json['results']), 4)


class APIItemDetailTestsPublicOrUserModels(MyAPITestCase):
    base_url = '/api/{}/{}/{}'

    def setUp(self):
        self.add_data()

    def test_public_item_returned_for_anonymous_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'decision', self.d1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['public'], True)
        self.assertEqual(response_json['summary_notes'], self.d1.summary_notes)

    def test_404_returned_if_no_item_for_anonymous_user(self):
        # stupidly high id number so its not likely to exist
        response = self.client.get(self.base_url.format('api_tests', 'decision', 100001))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_404_returned_for_private_item_for_anonymous_user(self):
        # ideally this would return 401 but that would means much more code being added into the decorator
        # The 404 is returned from the api class view
        # item with public set to False
        response = self.client.get(self.base_url.format('api_tests', 'decision', self.d2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)
        # item does not have public recorded
        response = self.client.get(self.base_url.format('api_tests', 'decision', self.d3.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_public_item_returned_for_logged_in_user(self):
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', self.d1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['public'], True)
        self.assertEqual(response_json['summary_notes'], self.d1.summary_notes)

    def test_private_item_returned_for_logged_in_user_if_owner(self):
        client = APIClient()
        login = client.login(username='user4@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', self.d2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['public'], False)
        self.assertEqual(response_json['summary_notes'], self.d2.summary_notes)

    def test_404_returned_for_logged_in_user_if_not_owner(self):
        # ideally this would return 403 but the filtering we use for item level permissions
        # means it doesn't get found
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', self.d2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_404_returned_if_no_item_for_logged_in_user(self):
        client = APIClient()
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', 100001))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_public_item_returned_for_logged_in_superuser(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', self.d1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['public'], True)
        self.assertEqual(response_json['summary_notes'], self.d1.summary_notes)

    def test_private_item_returned_for_logged_in_superuser_if_not_owner(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'decision', self.d2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['public'], False)
        self.assertEqual(response_json['summary_notes'], self.d2.summary_notes)


class APIItemListTestsPublicOrUserNoPublicField(MyAPITestCase):
    base_url = '/api/{}/{}/'
    # NB: There is no model that conforms to being 'public_or_user' availability
    # and with no public field because that should never happen. So I will
    # temporarily make an public one with no public field into a public_or_user one
    # using setUp and tearDown (which is why this test is in its own class)

    def setUp(self):
        models.Work.AVAILABILITY = 'public_or_user'
        self.add_data()

    def tearDown(self):
        models.Work.AVAILABILITY = 'public'

    def test_get_restricted_list_returns_500_for_anonymous_user_if_no_public_field_on_model(self):
        # 500 because it makes no sense and is a server config error really
        response = self.client.get(self.base_url.format('api_tests', 'work'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)


class APIItemListTestsPrivateModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        self.add_data()

    def test_get_private_list_returns_401_for_anonymous_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 401)

    def test_get_private_list_returns_owned_only_for_logged_in_regular_user(self):
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 1)
        self.assertEqual(len(response_json['results']), 1)
        self.assertEqual(response_json['results'][0]['score'], self.r2.score)

    def test_get_private_list_returns_all_for_app_superuser(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['count'], 6)
        self.assertEqual(len(response_json['results']), 6)


class APIItemDetailTestsPrivateModels(MyAPITestCase):
    base_url = '/api/{}/{}/{}'

    def setUp(self):
        self.add_data()

    def test_404_returned_if_no_item_for_anonymous_user(self):
        # use stupidly high id number so its not likely to exist
        response = self.client.get(self.base_url.format('api_tests', 'review', 100001))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_401_returned_for_existing_item_for_anonymous_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'review', self.r2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 401)

    def test_private_item_returned_for_logged_in_user_if_owner(self):
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review', self.r2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response_json['user'], self.u2.id)
        self.assertEqual(response_json['score'], self.r2.score)

    def test_404_returned_for_logged_in_user_if_not_owner(self):
        # ideally this would return 403
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review', self.r1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_404_returned_if_no_item_for_logged_in_user(self):
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review', 100001))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 404)

    def test_private_item_returned_for_logged_in_superuser_if_not_owner(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'review', self.r3.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertNotEqual(response_json['user'], self.u3.id)
        self.assertEqual(response_json['notes'], self.r3.notes)

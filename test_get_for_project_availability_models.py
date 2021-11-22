import json
from django.utils import timezone
from django.test import TestCase, Client
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.authtoken.models import Token
from unittest import skip
from api_tests import models

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
        self.u5 = self.add_user({'username': 'User5',
                                 'email': 'user5@example.com',
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

        p1_data = {'managing_editor': self.u4,
                   'status': 'in press',
                   'genre': 'sci-fi'}
        self.p1 = models.Project.objects.create(**p1_data)
        self.p1.work.add(self.w1.id)
        self.p1.editors.add(self.u2.id)
        self.p1.save()

        p2_data = {'managing_editor': self.u2,
                   'status': 'started',
                   'genre': 'historical'}
        self.p2 = models.Project.objects.create(**p2_data)
        self.p2.work.add(self.w3.id)
        self.p2.editors.add(self.u1.id)
        self.p2.editors.add(self.u3.id)
        self.p2.editors.add(self.u5.id)
        self.p2.save()

        pp1_data = {'project': self.p1,
                    'current_stage': 'print',
                    'notes': 'print run due next week',
                    'public': True,
                    'user': self.u1}
        self.pp1 = models.PublicationPlan.objects.create(**pp1_data)

        pp2_data = {'project': self.p1,
                    'current_stage': 'review',
                    'notes': 'third review due November',
                    'public': False,
                    'user': self.u2}
        self.pp2 = models.PublicationPlan.objects.create(**pp2_data)

        pp3_data = {'project': self.p2,
                    'current_stage': 'review',
                    'notes': 'third review due December',
                    'public': False,
                    'user': self.u4}
        self.pp3 = models.PublicationPlan.objects.create(**pp3_data)


class APIItemListTestsProjectsBadConfiguration(MyAPITestCase):
    base_url = '/api/{}/{}/'

    # manipulating a model to get this situation

    def setUp(self):
        models.Author.AVAILABILITY = 'project'

    def tearDown(self):
        models.Author.AVAILABILITY = 'public'

    def test_error_returned_if_model_availability_project_and_no_project_flag(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model configuation incompatible with API (code 10003)')


class APIItemListDetailProjectsBadConfiguration(MyAPITestCase):
    base_url = '/api/{}/{}/{}'

    # manipulating a model to get this situation

    def setUp(self):
        models.Author.AVAILABILITY = 'project'

    def tearDown(self):
        models.Author.AVAILABILITY = 'public'

    def test_error_returned_if_model_availability_project_and_no_project_flag(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'author', self.a1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model configuation incompatible with API (code 10003)')


class APIItemListTestsProjectModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        self.add_data()

    def test_get_project_list_returns_401_for_anonymous_user(self):
        response = self.client.get(self.base_url.format('api_tests', 'publicationplan'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_project_list_returns_400_if_no_project__id_in_request(self):
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['message'], 'Query not complete - Project must be specified')

    def test_get_project_list_returns_publicationplans_if_user_in_project_users(self):
        client = APIClient()
        login = client.login(username='user4@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('%s?project__id=%s' % (self.base_url.format('api_tests', 'publicationplan'),
                                                     self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        # user 4 is only in p1 and p1 has 2 publication plans so show both (only one is owned by u4)
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)

    def test_get_project_list_returns_publicationplans_if_user_in_multiple_projects(self):
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('%s?project__id=%s' % (self.base_url.format('api_tests', 'publicationplan'),
                                                     self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        # user 2 is in 2 projects but is asking for p1 and p1 has 2 publication plans so show both
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)

    def test_get_project_list_returns_no_publicationplans_if_user_not_in_projects(self):
        client = APIClient()
        login = client.login(username='user5@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('%s?project__id=%s' % (self.base_url.format('api_tests', 'publicationplan'),
                                                     self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        # user5 is not in any projects so no data returned
        self.assertEqual(response_json['count'], 0)
        self.assertEqual(len(response_json['results']), 0)

    def test_get_project_list_returns_all_project_publicationplans_for_superuser_if_not_in_requested_project(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('%s?project__id=%s' % (self.base_url.format('api_tests', 'publicationplan'),
                                                     self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        # user5 is not in requested project but is superuser so gets decisions for this project only
        self.assertEqual(response_json['count'], 2)
        self.assertEqual(len(response_json['results']), 2)


class APIItemListTestsProjectOrUserBadConfiguration(MyAPITestCase):
    base_url = '/api/{}/{}/'
    # manipulate a model to create this situation

    def setUp(self):
        models.Author.AVAILABILITY = 'project_or_user'

    def tearDown(self):
        models.Author.AVAILABILITY = 'public'

    def test_error_returned_if_model_availability_project_and_no_project_flag(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'author'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model configuation incompatible with API (code 10003)')


class APIItemListTestsProjectOrUserModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    # there is no test model that matches this so adapting one for this test

    def setUp(self):
        self.add_data()
        models.PublicationPlan.AVAILABILITY = 'project_or_user'

    def tearDown(self):
        models.PublicationPlan.AVAILABILITY = 'project'

    def test_get_project_list_returns_401_for_anonymous_user(self):
        client = APIClient()
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['content-type'], 'application/json')

    def test_error_for_logged_in_user_if_no_project(self):
        client = APIClient()
        # user in projects
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['message'], 'Query not complete - Project must be specified')

    def test_return_for_logged_in_user_if_project(self):
        # user in project with 2 publication plans
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 2)

        # another example where user is owner of a publication plan but not in the project and in another project
        # this should returned the owned item in the requested project
        login = client.login(username='user4@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 1)

        # only one item returned if 2 items in project and user is not in project but owns one item
        login = client.login(username='user1@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 1)

    def test_404_error_if_user_not_in_project_and_not_owner(self):
        client = APIClient()
        login = client.login(username='user5@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 0)

    def test_superuser_get_everything_requested(self):
        client = APIClient()
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 2)


class APIItemListTestsPublicOrProjectBadConfigurationPublicMissing(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        models.Author.AVAILABILITY = 'public_or_project'

    def tearDown(self):
        models.Author.AVAILABILITY = 'public'

    def test_error_returned_if_no_public_or_project_in_model(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'author'), self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model configuation incompatible with API (code 10002)')


class APIItemListTestsPublicOrProjectBadConfigurationProjectMissing(MyAPITestCase):
    base_url = '/api/{}/{}/'

    def setUp(self):
        models.Decision.AVAILABILITY = 'public_or_project'

    def tearDown(self):
        models.Decision.AVAILABILITY = 'public_or_user'

    def test_error_returned_if_public_but_no_project_in_model(self):
        self.add_data()
        client = APIClient()
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'decision'), self.d1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['message'],
                         'Internal server error - model configuation incompatible with API (code 10002)')


class APIItemListTestsPublicOrProjectModels(MyAPITestCase):
    base_url = '/api/{}/{}/'

    # there is no test model that matches this so adapting one for this test

    def setUp(self):
        self.add_data()
        models.PublicationPlan.AVAILABILITY = 'public_or_project'

    def tearDown(self):
        models.PublicationPlan.AVAILABILITY = 'project'

    def test_get_list_returns_public_items_for_anonymous_user(self):
        client = APIClient()
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 1)

    def test_get_list_returns_public_items_if_no_project(self):
        client = APIClient()
        # user in projects
        login = client.login(username='user2@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 1)

    def test_get_list_returns_everything_for_superuser(self):
        client = APIClient()
        # user in projects
        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get(self.base_url.format('api_tests', 'publicationplan'))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 3)

    def test_get_list_returns_project_items_if_project(self):
        client = APIClient()
        # user in projects
        login = client.login(username='user5@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p2.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 1)
        # check that ownership of item does not override project settings
        # (this should never happen in reality and suggests an incorrect availability but it tests code)
        login = client.login(username='user4@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.get('{}?project__id={}'.format(self.base_url.format('api_tests', 'publicationplan'),
                                                         self.p1.id))
        response_json = json.loads(response.content.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['count'], 2)

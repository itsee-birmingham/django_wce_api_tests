import json
import datetime
from unittest import skip
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory
from api_tests import models

User = get_user_model()


class APIPostTests(APITestCase):
    base_url = '/api/{}/{}/'

    def addDataManagerUser(self, credentials):
        try:
            g2 = Group.objects.filter(name='data_managers')[0]
        except IndexError:
            g2 = Group(name='data_managers')
            g2.save()
            self.add_data_manager_permissions(g2)
        user = User.objects.create_user(**credentials)
        user.groups.add(g2)
        user.save()
        return user

    def addDataEditorUser(self, credentials):
        try:
            g2 = Group.objects.filter(name='data_editors')[0]
        except IndexError:
            g2 = Group(name='data_editors')
            g2.save()
            self.add_data_editor_permissions(g2)
        user = User.objects.create_user(**credentials)
        user.groups.add(g2)
        user.save()
        return user

    def add_user(self, credentials):
        if 'public_name' in credentials:
            public_name = credentials['public_name']
            del credentials['public_name']
            user = User.objects.create_user(**credentials)
            user.save()
            user.public_name = public_name
            user.save()
        else:
            user = User.objects.create_user(**credentials)
            user.save()
        return user

    def add_superuser(self, credentials):
        g1 = Group(name='api_tests_superusers')
        g1.save()
        if 'public_name' in credentials:
            public_name = credentials['public_name']
            del credentials['public_name']
            user = User.objects.create_user(**credentials)
            user.groups.add(g1)
            user.save()
            user.public_name = public_name
            user.save()
        else:
            user = User.objects.create_user(**credentials)
            user.groups.add(g1)
            user.save()
        return user

    def add_data_editor_permissions(self, group):
        content_type = ContentType.objects.get_for_model(models.Author)
        permission = Permission.objects.get(content_type=content_type, codename='add_author')
        group.permissions.add(permission)
        content_type = ContentType.objects.get_for_model(models.Author)
        permission = Permission.objects.get(content_type=content_type, codename='change_author')
        group.permissions.add(permission)
        # group.permissions.add(Permission.objects.get(codename='add_edition'))
        # group.permissions.add(Permission.objects.get(codename='change_edition'))
        # group.permissions.add(Permission.objects.get(codename='add_series'))
        # group.permissions.add(Permission.objects.get(codename='change_series'))
        # group.permissions.add(Permission.objects.get(codename='add_onlinecorpus'))
        # group.permissions.add(Permission.objects.get(codename='change_onlinecorpus'))
        # # work has to take into account content type because of a clash with the transcriptions.work model
        # content_type = ContentType.objects.get_for_model(models.Work)
        # permission = Permission.objects.get(content_type=content_type, codename='add_work')
        # group.permissions.add(permission)
        # permission = Permission.objects.get(content_type=content_type, codename='change_work')
        # group.permissions.add(permission)
        group.save()

    def add_data_manager_permissions(self, group):
        content_type = ContentType.objects.get_for_model(models.Author)
        permission = Permission.objects.get(content_type=content_type, codename='add_author')
        group.permissions.add(permission)
        content_type = ContentType.objects.get_for_model(models.Author)
        permission = Permission.objects.get(content_type=content_type, codename='change_author')
        group.permissions.add(permission)
        content_type = ContentType.objects.get_for_model(models.Author)
        permission = Permission.objects.get(content_type=content_type, codename='delete_author')
        group.permissions.add(permission)
        group.save()

    def test_getUser(self):
        user = self.addDataEditorUser({'username': 'testuser@example.com',
                                       'email': 'testuser@example.com',
                                       'public_name': 'Test User',
                                       'password': 'xyz'})
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)
        response = client.get('/api/whoami')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], user.id)

    # @skip('')
    def test_POSTAuthor(self):
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 0)
        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'active': True
                   }
        response = self.client.post('%screate' % self.base_url.format('api_tests', 'author'), a1_data)
        # we should not be able to create unless we are logged in - 403 Authentication credentials were not provided.
        self.assertEqual(response.status_code, 403)

        # now login
        user = self.addDataEditorUser({'username': 'testuser@example.com',
                                       'email': 'testuser@example.com',
                                       'public_name': 'Test User',
                                       'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.add_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)

        response = client.post('%screate' % self.base_url.format('api_tests', 'author'),
                               json.dumps(a1_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        self.assertEqual(authors[0].identifier, 'JS1')
        self.assertEqual(authors[0].created_by, user.public_name)

        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        client.logout()

        # now try again but as a different user with no full_name.
        user2 = self.addDataEditorUser({'username': 'testuser2@example.com',
                                        'email': 'testuser2@example.com',
                                        'password': 'xyz'})
        self.assertTrue(user2.has_perm('api_tests.add_author'))
        client2 = APIClient()
        login = client2.login(username='testuser2@example.com', password='xyz')
        self.assertEqual(login, True)

        # use the same data as added by someone else
        response = client2.post('%screate' % self.base_url.format('api_tests', 'author'),
                                json.dumps(a1_data), content_type='application/json')
        # it does not work because identifier must be unique
        self.assertEqual(response.status_code, 400)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)

        # now try with different data
        a2_data = {'identifier': 'JS2',
                   'name': 'Jane Smart',
                   'age': 34,
                   'active': True
                   }
        response = client2.post('%screate' % self.base_url.format('api_tests', 'author'),
                                json.dumps(a2_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 2)
        author = models.Author.objects.filter(identifier='JS2')[0]
        self.assertEqual(author.identifier, 'JS2')
        self.assertEqual(author.created_by, user2.username)

    # @skip('')
    def test_PATCHAuthorPartial(self):
        # make an author to modify
        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'date_joined': datetime.datetime.strptime('2010 4 6', '%Y %m %d').date(),
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)

        response = self.client.patch('%supdate/%s' % (self.base_url.format('api_tests', 'author'), a1.id),
                                     json.dumps({'name': 'My new name'}), content_type='application/json')
        # we should not be able to modify unless we are logged in - 403 Authentication credentials were not provided.
        self.assertEqual(response.status_code, 403)

        # now login
        user = self.addDataEditorUser({'username': 'testuser@example.com',
                                       'email': 'testuser@example.com',
                                       'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.change_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)

        response = client.patch('%supdate/%s' % (self.base_url.format('api_tests', 'author'), a1.id),
                                json.dumps({'name': 'My new name'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()

        # make sure we are getting the full object back not just the changed fields
        self.assertTrue('age' in response_json)
        self.assertEqual(response_json['age'], 28)
        self.assertTrue('active' in response_json)
        self.assertEqual(response_json['active'], True)

        # make sure the changes were applied
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        self.assertEqual(authors[0].name, 'My new name')
        self.assertEqual(authors[0].last_modified_by, 'testuser@example.com')

    def test_PUTAuthorNoChange(self):
        # make an author to modify
        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'date_joined': datetime.datetime.strptime('2010 4 6', '%Y %m %d').date(),
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)
        # we need to get the stored version because otherwise the creation time strings are different!
        response = self.client.get(self.base_url.format('api_tests', 'author', a1.id))
        response_json = json.loads(response.content.decode('utf8'))

        user = self.addDataEditorUser({'username': 'testuser',
                                       'email': 'testuser@example.com',
                                       'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.change_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)
        a1_data['id'] = a1.id
        response = client.put('%supdate/%s' % (self.base_url.format('api_tests', 'author'), a1.id),
                              json.dumps(response_json['results'][0]), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        self.assertEqual(authors[0].name, 'John Smith')
        self.assertEqual(authors[0].last_modified_by, '')

    # @skip('')
    def test_PUTAuthorChange(self):
        # make an author to modify
        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'date_joined': datetime.datetime.strptime('2010 4 6', '%Y %m %d').date(),
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)
        # we need to get the stored version because otherwise the creation time strings are different!
        response = self.client.get(self.base_url.format('api_tests', 'author', a1.id))
        response_json = json.loads(response.content.decode('utf8'))
        response_json['results'][0]['name'] = 'My new name'

        user = self.addDataEditorUser({'username': 'testuser',
                                       'email': 'testuser@example.com',
                                       'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.add_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)
        a1_data['id'] = a1.id
        response = client.put('%supdate/%s' % (self.base_url.format('api_tests', 'author'), a1.id),
                              json.dumps(response_json['results'][0]), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        self.assertEqual(authors[0].name, 'My new name')
        self.assertEqual(authors[0].last_modified_by, 'testuser@example.com')
        self.assertNotEqual(authors[0].last_modified_time, None)

    def test_DELETEAuthor(self):
        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'date_joined': datetime.datetime.strptime('2010 4 6', '%Y %m %d').date(),
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)
        a2_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS2',
                   'name': 'Jane Smart',
                   'age': 34,
                   'active': True
                   }
        a2 = models.Author.objects.create(**a2_data)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 2)
        client = APIClient()
        response = client.delete('%sdelete/%s' % (self.base_url.format('api_tests', 'author'), a1.id))
        self.assertEqual(response.status_code, 403)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 2)
        user = self.addDataEditorUser({'username': 'testuser',
                                       'email': 'testuser@example.com',
                                       'password': 'xyz'})
        self.assertFalse(user.has_perm('api_tests.delete_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)
        response = client.delete('%sdelete/%s' % (self.base_url.format('api_tests', 'author'), a1.id))
        self.assertEqual(response.status_code, 403)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 2)
        user = self.addDataManagerUser({'username': 'testuser2',
                                        'email': 'testuser2@example.com',
                                        'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.delete_author'))
        client2 = APIClient()
        login = client2.login(username='testuser2@example.com', password='xyz')
        self.assertEqual(login, True)
        response = client2.delete('%sdelete/%s' % (self.base_url.format('api_tests', 'author'), a1.id))
        self.assertEqual(response.status_code, 204)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)
        self.assertEqual(authors[0].identifier, a2.identifier)

    def test_DELETEWithDeps(self):

        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'date_joined': datetime.datetime.strptime('2010 4 6', '%Y %m %d').date(),
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)

        w1_data = {'identifier': 'W1',
                   'title': 'My Title',
                   'author': a1}
        w1 = models.Work.objects.create(**w1_data)

        user = self.addDataManagerUser({'username': 'testuser',
                                        'email': 'testuser@example.com',
                                        'password': 'xyz'})
        self.assertTrue(user.has_perm('api_tests.delete_author'))
        client = APIClient()
        login = client.login(username='testuser@example.com', password='xyz')
        self.assertEqual(login, True)
        response = client.delete('%sdelete/%s' % (self.base_url.format('api_tests', 'author'), a1.id))
        self.assertEqual(response.status_code, 500)
        authors = models.Author.objects.all()
        self.assertTrue(len(authors) == 1)

    def test_M2MDelete(self):

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

        a1_data = {'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'active': True
                   }
        self.a1 = models.Author.objects.create(**a1_data)

        w1_data = {'identifier': 'W1',
                   'title': 'My First Book',
                   'author': self.a1
                   }
        self.w1 = models.Work.objects.create(**w1_data)

        p1_data = {'managing_editor': self.u4,
                   'status': 'in press',
                   'genre': 'sci-fi'}
        self.p1 = models.Project.objects.create(**p1_data)
        self.p1.work.add(self.w1.id)
        self.p1.editors.add(self.u2.id)
        self.p1.editors.add(self.u3.id)
        self.p1.save()

        # check not logged in users cannot delete
        projects = models.Project.objects.all()
        self.assertTrue(len(projects) == 1)
        self.assertTrue(len(projects[0].editors.all()) == 2)
        client = APIClient()
        urlstring = '%s%s/editors/delete/user/%s' % (self.base_url.format('api_tests', 'project'),
                                                     self.p1.id,
                                                     self.u2.id)

        response = client.patch('%s%s/editors/delete/user/%s' % (self.base_url.format('api_tests', 'project'),
                                                                 self.p1.id,
                                                                 self.u2.id))
        self.assertEqual(response.status_code, 403)
        # check everything is still the same
        projects = models.Project.objects.all()
        self.assertTrue(len(projects) == 1)
        self.assertTrue(len(projects[0].editors.all()) == 2)

        login = client.login(username='user3@example.com', password='secret')
        self.assertEqual(login, True)
        response = client.patch('%s%s/editors/delete/user/%s' % (self.base_url.format('api_tests', 'project'),
                                                                 self.p1.id,
                                                                 self.u2.id))
        print(response)
        # projects = models.Project.objects.all()
        # self.assertTrue(len(projects) == 1)
        # self.assertTrue(len(projects[0].editors.all()) == 1)

import sys
import os
import json
import datetime
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from rest_framework.request import Request
from rest_framework.test import APIClient
from django.db.models import Q
from api import views
from api.views import SelectPagePaginator
from api import models
from api.serializers import SimpleSerializer
from api_tests import models
from api_tests import serializers

User = get_user_model()


class APIHelperTests(TestCase):

    def addDataManagerUser(self, credentials):
        user = User.objects.create_user(**credentials)
        user.save()
        return user

    def test_getCount(self):
        # with a query set
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
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

        query_set = models.Author.objects.all()
        count = views.getCount(query_set)
        self.assertEqual(count, 2)

        # and with a list
        test_list = ['item', 'item']
        count = views.getCount(test_list)
        self.assertEqual(count, 2)

    def test_getDateField(self):

        expected_date = datetime.datetime.strptime('1900', '%Y').date()
        date = views.getDateField('>', '>1900')
        self.assertEqual(date, expected_date)

        expected_date = datetime.datetime.strptime('1900 12 31', '%Y %m %d').date()
        date = views.getDateField('<', '<1900')
        self.assertEqual(date, expected_date)

        # test what happens with bad data
        expected_date = '=1900'
        date = views.getDateField('<', '=1900')
        self.assertEqual(date, expected_date)

    def test_getQueryTuple(self):
        # this is testing the code and a few random selections from the operator_lookup dictionary
        # it is not really designed to test the dictionary - I think it is a constant
        expected_return = ('name__istartswith', 'Test')
        query_tuple = views.getQueryTuple('TextField', 'name', 'Test*|i')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('name__contains', 'Test')
        query_tuple = views.getQueryTuple('CharField', 'name', '*Test*')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('age__lte', '9')
        query_tuple = views.getQueryTuple('IntegerField', 'age', '<=9')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('active', False)
        query_tuple = views.getQueryTuple('BooleanField', 'active', 'false')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('genres__contains', ['list'])
        query_tuple = views.getQueryTuple('ArrayField', 'genres', 'list')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('genres__len__gt', '1')
        query_tuple = views.getQueryTuple('ArrayField', 'genres', '_gt1')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('date_joined__gt', datetime.datetime.strptime('1900', '%Y').date())
        query_tuple = views.getQueryTuple('DateField', 'date_joined', '>1900')
        self.assertEqual(expected_return, query_tuple)

        expected_return = ('test', 'value')
        query_tuple = views.getQueryTuple('OtherField', 'test', 'value')
        self.assertEqual(expected_return, query_tuple)

        expected_return = None
        query_tuple = views.getQueryTuple('OtherField', 'test', '')
        self.assertEqual(expected_return, query_tuple)

    def test_getRelatedModel(self):
        model_instance = views.getRelatedModel(models.Work, 'author__name')
        self.assertEqual(model_instance, models.Author)

    def test_getRelatedFieldType(self):
        related_field_type = views.getRelatedFieldType(models.Work, 'title')
        self.assertEqual(related_field_type, None)

        related_field_type = views.getRelatedFieldType(models.Work, 'author__name')
        self.assertEqual(related_field_type, 'TextField')

        related_field_type = views.getRelatedFieldType(models.Edition, 'work__author__name')
        self.assertEqual(related_field_type, 'TextField')

        related_field_type = views.getRelatedFieldType(models.Work, 'author__nonsense')
        self.assertEqual(related_field_type, None)

    def test_getFieldFilters(self):
        rf = RequestFactory()

        # I will test most of the code with simple author abbreviation searches
        # it gives us decent line coverage and keeps the test code readable
        # to get better branch combination coverage there probably needs to be some complex test cases

        # positive value in filter mode
        expected_query = Q()
        expected_query &= Q(('identifier__startswith', 'J'))
        expected_query = [expected_query]
        request = rf.get('/api/citations/author?identifier=J*')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Author, 'filter')
        self.assertEqual(str(expected_query), str(query))

        # negative value in exclude mode
        expected_query = Q()
        expected_query &= Q(('identifier__startswith', 'J'))
        expected_query = [expected_query]
        request = rf.get('/api/citations/author?identifier=!J*')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Author, 'exclude')
        self.assertEqual(str(expected_query), str(query))

        # negative value in filter mode - which should return an empty query
        expected_query = Q()
        expected_query = [expected_query]
        request = rf.get('/api/citations/author?identifier=!J*')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Author, 'filter')
        self.assertEqual(str(expected_query), str(query))

        # now test list filters
        expected_query = Q()
        subquery = Q()
        subquery |= Q(('identifier', 'JS1'))
        subquery |= Q(('identifier', 'JS2'))
        expected_query &= subquery
        expected_query = [expected_query]
        request = rf.get('/api/citations/author?identifier=JS1,JS2')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Author, 'filter')
        self.assertEqual(str(expected_query), str(query))

        # positive value in filter mode with foreign key
        expected_query = Q()
        expected_query &= Q(('author__identifier__startswith', 'J'))
        expected_query = [expected_query]
        request = rf.get('/api/citations/work/?author__identifier=J*')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Work, 'filter')
        self.assertEqual(str(expected_query), str(query))

        # positive value in filter mode with nonsense field
        # should produce empty query so it does not stop results returning
        expected_query = Q()
        expected_query &= Q()
        expected_query = [expected_query]
        request = rf.get('/api/citations/work/?nonsense=J*')
        requestQuery = dict(request.GET)
        query = views.getFieldFilters(requestQuery, models.Work, 'filter')
        self.assertEqual(str(expected_query), str(query))

    def test_getEtag(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
                   'active': True
                   }
        a1 = models.Author.objects.create(**a1_data)
        rf = RequestFactory()
        request = Request(rf.get('/api/api_tests/author/{}'.format(a1.id)))
        etag = views.get_etag(request)
        self.assertEqual(etag, '*')
        etag = views.get_etag(request, 'api_tests', 'author', a1.id)
        self.assertEqual(etag, '1')

    def test_SelectPagePaginator(self):

        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
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
        a3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS3',
                   'name': 'Jenny Stopes',
                   'age': 57,
                   'active': True
                   }
        a3 = models.Author.objects.create(**a3_data)

        rf = RequestFactory()
        request = Request(rf.get('/api/citations/author/?limit=2'))
        paginator = SelectPagePaginator()
        result = paginator.paginate_queryset_and_get_page(models.Author.objects.all(), request, index_required=3)
        self.assertIn(a3, result[0])
        self.assertEqual(result[1], 2)

        # if we are showing all records anyway (this will actually default to 100 because of your default)
        request = Request(rf.get('/api/citations/author'))
        paginator = SelectPagePaginator()
        result = paginator.paginate_queryset_and_get_page(models.Author.objects.all(), request, index_required=3)
        self.assertEqual(len(result[0]), 3)

        # if we are showing all records anyway (this will actually default to 100 because of your default)
        request = Request(rf.get('/api/citations/works'))
        paginator = SelectPagePaginator()
        result = paginator.paginate_queryset_and_get_page(models.Work.objects.all(), request, index_required=3)
        self.assertEqual(result, [])


# these are tests for specific functions in the model class I want to check
# rather than testing the whole view at once
class ItemListUnitTests(TestCase):

    def test_get_serializer_class(self):

        item_list_view = views.ItemList()
        item_list_view.kwargs = {'app': 'api_tests', 'model': 'author'}
        serializer_class = item_list_view.get_serializer_class()
        self.assertEqual(serializer_class, serializers.AuthorSerializer)

        item_list_view = views.ItemList()
        item_list_view.kwargs = {'app': 'api_tests', 'model': 'work'}
        serializer_class = item_list_view.get_serializer_class()
        self.assertEqual(serializer_class, serializers.WorkSerializer)

    def test_get_offset_required(self):
        a1_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'JS1',
                   'name': 'John Smith',
                   'age': 28,
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
        a3_data = {'created_by': 'cat',
                   'created_time': timezone.now(),
                   'identifier': 'AS3',
                   'name': 'Anna Stopes',
                   'age': 57,
                   'active': True
                   }
        a3 = models.Author.objects.create(**a3_data)
        item_list_view = views.ItemList()

        queryset = models.Author.objects.all().order_by('name')
        position = item_list_view.get_offset_required(queryset, a1.id)
        self.assertEqual(position, 2)

        position = item_list_view.get_offset_required(queryset, a3.id)
        self.assertEqual(position, 0)

        position = item_list_view.get_offset_required(queryset, 99)
        self.assertEqual(position, 0)


class ItemDetailUnitTests(TestCase):

    def test_get_serializer_class(self):

        item_detail_view = views.ItemDetail()
        item_detail_view.kwargs = {'app': 'api_tests', 'model': 'author'}
        serializer_class = item_detail_view.get_serializer_class()
        self.assertEqual(serializer_class, serializers.AuthorSerializer)

        item_detail_view = views.ItemList()
        item_detail_view.kwargs = {'app': 'api_tests', 'model': 'work'}
        serializer_class = item_detail_view.get_serializer_class()
        self.assertEqual(serializer_class, serializers.WorkSerializer)
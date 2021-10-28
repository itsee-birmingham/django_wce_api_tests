from django.db import models
from django.conf import settings
from api.models import BaseModel


class Author (BaseModel):

    AVAILABILITY = 'public'

    REQUIRED_FIELDS = ['identifier', 'name']

    SERIALIZER = 'AuthorSerializer'

    identifier = models.TextField('Identifier', unique=True)
    name = models.TextField('Name', blank=True)
    age = models.IntegerField('Age', null=True, blank=True)
    date_joined = models.DateField('Date Joined', null=True)
    active = models.BooleanField('Active', null=True)

    def get_serialization_fields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Author._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    class Meta:
        ordering = ['identifier']


class Work (BaseModel):

    AVAILABILITY = 'public'

    SERIALIZER = 'WorkSerializer'

    identifier = models.TextField('Identifier', blank=True)
    title = models.TextField('Title', blank=True)
    author = models.ForeignKey('Author',
                               models.PROTECT,
                               related_name='works')
    # reviews = models.ManyToManyField(Review,
    #                                  null=True,
    #                                  on_delete=models.SET_NULL,
    #                                  related_name='works')

    def get_serialization_fields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Work._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Review (BaseModel):

    AVAILABILITY = 'private'

    SERIALIZER = 'ReviewSerializer'

    notes = models.TextField('Notes', null=True, blank=True)
    score = models.IntegerField('Score', null=True, blank=True)
    work = models.ForeignKey('Work',
                             models.PROTECT,
                             related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             models.PROTECT,
                             related_name='reviewers')

    def get_serialization_fields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Review._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Decision (BaseModel):

    AVAILABILITY = 'public_or_user'

    work = models.ForeignKey('Work',
                             models.PROTECT,
                             related_name='decision')
    accept = models.BooleanField(null=True)
    summary_notes = models.TextField('Notes', null=True, blank=True)
    public = models.BooleanField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             models.PROTECT,
                             related_name='decider')

    def get_serialization_fields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Decision._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Edition (BaseModel):

    AVAILABILITY = 'public'

    identifier = models.TextField('Identifier', blank=True)
    work = models.ForeignKey('Work',
                             models.PROTECT,
                             related_name='editions')
    year = models.IntegerField('Year', null=True)
    place = models.TextField('Place', blank=True)
    volume = models.TextField('Volume', blank=True)

    def get_serialization_fields():
        fields = '__all__'
        return fields

    def get_fields():
        data = {}
        fields = list(Edition._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

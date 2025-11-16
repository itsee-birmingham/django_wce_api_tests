"""These models are made up purely for testing and are loosly bsaed on models that might be needed by publishers."""

from api.models import BaseModel
from django.conf import settings
from django.db import models


class Author(BaseModel):
    """The author of a book."""

    AVAILABILITY = 'public'

    REQUIRED_FIELDS = ['identifier', 'name']

    SERIALIZER = 'AuthorSerializer'

    identifier = models.TextField('Identifier', unique=True)
    name = models.TextField('Name', blank=True)
    age = models.IntegerField('Age', null=True, blank=True)
    date_joined = models.DateField('Date Joined', null=True)
    active = models.BooleanField('Active', null=True)

    def get_fields():
        data = {}
        fields = list(Author._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    class Meta:
        ordering = ['identifier']


class Work(BaseModel):
    """A book."""

    AVAILABILITY = 'public'

    SERIALIZER = 'WorkSerializer'

    identifier = models.TextField('Identifier', blank=True)
    title = models.TextField('Title', blank=True)
    author = models.ForeignKey('Author', models.PROTECT, related_name='works')

    def get_fields():
        data = {}
        fields = list(Work._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Review(BaseModel):
    """A reviewers review of a book."""

    AVAILABILITY = 'private'

    SERIALIZER = 'ReviewSerializer'

    notes = models.TextField('Notes', null=True, blank=True)
    score = models.IntegerField('Score', null=True, blank=True)
    work = models.ForeignKey('Work', models.PROTECT, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='reviewers')

    def get_fields():
        data = {}
        fields = list(Review._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Decision(BaseModel):
    """An editors publication decision about a book."""

    AVAILABILITY = 'public_or_user'

    SERIALIZER = 'DecisionSerializer'

    work = models.ForeignKey('Work', models.PROTECT, related_name='decision')
    accept = models.BooleanField(null=True)
    summary_notes = models.TextField('Notes', null=True, blank=True)
    public = models.BooleanField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='decider')

    def get_fields():
        data = {}
        fields = list(Decision._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Project(BaseModel):
    """A managing editors project containing the books they are responsible for reviewing and publishing."""

    AVAILABILITY = 'public'

    managing_editor = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, related_name='manager')
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='editor_of', blank=True)
    status = models.TextField('Status', null=True, blank=True)
    genre = models.TextField('Genre', null=True, blank=True)
    work = models.ManyToManyField('Work', related_name='included_in', blank=True)

    def get_fields():
        data = {}
        fields = list(Decision._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

    def get_user_fields():
        user_fields = ['editors', 'managing_editor']
        data = {}
        fields = list(Project._meta.get_fields(include_hidden=True))
        for field in fields:
            if field.name in user_fields:
                data[field.name] = field.get_internal_type()
        return data


class PublicationPlan(BaseModel):
    """The publication plan for a book tracking its progress."""

    AVAILABILITY = 'project'

    SERIALIZER = 'PublicationPlanSerializer'

    project = models.ForeignKey('Project', models.PROTECT, related_name='plan')
    current_stage = models.TextField('Stage', null=True, blank=True)
    notes = models.TextField('Notes', null=True, blank=True)
    public = models.BooleanField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, null=True, related_name='plan_creator')
    editors = models.ManyToManyField('Editor', blank=True)

    def get_fields():
        data = {}
        fields = list(PublicationPlan._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Editor(BaseModel):
    """An editor of a book."""

    AVAILABILITY = 'logged_in'

    SERIALIZER = 'EditorSerializer'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT, null=True)
    active = models.BooleanField(null=True)

    def get_fields():
        data = {}
        fields = list(Editor._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data


class Edition(BaseModel):
    """An edition of a book."""

    SERIALIZER = 'EditionSerializer'

    identifier = models.TextField('Identifier', blank=True)
    work = models.ForeignKey('Work', models.PROTECT, related_name='editions')
    year = models.IntegerField('Year', null=True)
    place = models.TextField('Place', blank=True)
    volume = models.TextField('Volume', blank=True)

    def get_fields():
        data = {}
        fields = list(Edition._meta.get_fields(include_hidden=True))
        for field in fields:
            data[field.name] = field.get_internal_type()
        return data

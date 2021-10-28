from rest_framework import serializers
from api import serializers as api_serializers
from . import models


class AuthorSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Author


class WorkSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Work


class ReviewSerializer(api_serializers.BaseModelSerializer):

    class Meta:
        model = models.Review

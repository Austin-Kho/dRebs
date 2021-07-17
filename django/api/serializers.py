from rest_framework import serializers

from books.models import Book, Subject, Image


class BookSerializer(serializers.HyperlinkedModelSerializer):
    subjects = serializers.HyperlinkedRelatedField(many=True, view_name='api:subject-detail')

    class Meta:
        model = Book
        fields = ('url', 'pk', 'seq', 'title')



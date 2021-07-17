from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework.reverse import reverse

from books.models import Book, Subject, Image

from . serializers import BookSerializer, SubjectSerializer


class BookList(generics.ListCreateAPIView):
    name = 'book-list'
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'book-detail'
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class SubjectList(generics.ListCreateAPIView):
    name = 'subject-list'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'subject-detail'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

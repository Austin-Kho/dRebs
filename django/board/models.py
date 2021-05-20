from django.db import models
from django.conf import settings


class Group(models.Model):
    key = models.CharField('키', max_length=100)
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='관리자')


class Board(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    key = models.CharField('키', max_length=100)
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    # search = models.PositiveSmallIntegerField('검색수')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='관리자')


class Category(models.Model):
    board = models.ForeignKey(Board, on_delete=models.SET_NULL)
    key = models.CharField('키', max_length=255)
    value = models.CharField('값', max_length=255)
    parent = models.CharField('부모카테고리', max_length=255)
    order = models.PositiveSmallIntegerField('순서')


class Post(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    is_notice = models.BooleanField('공지사항', default=False)
    title = models.CharField('제목', max_length=255)
    content = models.TextField('내용')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # num = models.PositiveIntegerField()
    reply = models.CharField('', max_length=10)
    html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))
    ip = models.GenericIPAddressField()
    images = models.ImageField()
    files = models.FilePathField()
    soft_delete = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

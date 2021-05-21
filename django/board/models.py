from django.db import models
from django.conf import settings


class Group(models.Model):
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='관리자')


class Board(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='관리자')


class Category(models.Model):
    board = models.ForeignKey(Board, on_delete=models.SET_NULL)
    name = models.CharField('값', max_length=255)
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
    like = models.PositiveIntegerField()
    dislike = models.PositiveIntegerField()
    blame = models.PositiveSmallIntegerField()
    soft_delete = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    tag = models.CharField('태그', max_length=100)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reply = models.CharField('', max_length=20)
    html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))
    secret = models.BooleanField(default=False)
    content = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField('패스워드', max_length=255)
    ip = models.GenericIPAddressField()
    like = models.PositiveIntegerField()
    dislike = models.PositiveIntegerField()
    blame = models.PositiveSmallIntegerField()
    soft_delete = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

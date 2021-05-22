from django.db import models
from django.conf import settings


class Group(models.Model):
    url = models.CharField('주소', max_length=20)
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    manager = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='관리자')


class Board(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    url = models.CharField('주소', max_length=20)
    name = models.CharField('명칭', max_length=255)
    order = models.PositiveSmallIntegerField('순서')
    search_able = models.BooleanField('검색사용', default=True)
    manager = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='관리자')


class Category(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    name = models.CharField('값', max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL)
    order = models.PositiveSmallIntegerField('순서')


class Post(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    is_notice = models.CharField('공지사항', choices=(('', '일반'), ('1', '공지'), ('2', '전체공지')), default='')
    title = models.CharField('제목', max_length=255)
    content = models.TextField('내용')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    secret = models.BooleanField('비밀글', default=False)
    password = models.CharField('패스워드', max_length=255, null=True, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_hide_comment = models.BooleanField('댓글숨기기', default=False)
    hit = models.PositiveIntegerField('조회수')
    like = models.PositiveIntegerField('추천')
    dislike = models.PositiveIntegerField('비추천')
    blame = models.PositiveSmallIntegerField('신고하기')
    files = models.FileField()
    images = models.ImageField()
    link_urls = models.URLField()
    ip = models.GenericIPAddressField('아이피')
    device = models.CharField('기기', max_length=10)
    soft_delete = models.DateTimeField(null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # number = models.PositiveIntegerField()
    # reply = models.CharField('댓글', max_length=10)
    # link_count = models.PositiveIntegerField()
    # receive_email = models.BooleanField()
    # html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(null=True, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    secret = models.BooleanField('비밀글', default=False)
    password = models.CharField('패스워드', max_length=255, null=True, default='')
    like = models.PositiveIntegerField('추천')
    dislike = models.PositiveIntegerField('비추천')
    blame = models.PositiveSmallIntegerField('신고하기')
    ip = models.GenericIPAddressField('아이피')
    device = models.CharField('기기', max_length=10)
    soft_delete = models.DateTimeField(null=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # number = models.PositiveIntegerField()
    # reply = models.CharField('댓글', max_length=10)
    # html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))


class Tag(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    tag = models.CharField('태그', max_length=100)
    post = models.ManyToManyField(Post)

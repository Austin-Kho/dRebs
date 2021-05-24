import hashlib
from django.db import models
from datetime import datetime
from django.conf import settings


class Group(models.Model):
    name = models.CharField('이름', max_length=255)
    manager = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name='관리자')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = '01. 그룹 관리'
        verbose_name_plural = '01. 그룹 관리'


class Board(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='그룹')
    url = models.CharField('uri', max_length=20)
    name = models.CharField('이름', max_length=255)
    order = models.PositiveSmallIntegerField('정렬 순서', default=0)
    search_able = models.BooleanField('검색사용', default=True)
    manager = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name='관리자')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = '02. 게시판 관리'
        verbose_name_plural = '02. 게시판 관리'


class Partition(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    name = models.CharField('이름', max_length=100)
    project = models.ForeignKey('rebs_project.Project', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='프로젝트')
    order = models.PositiveSmallIntegerField('정렬 순서', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = '03. 파티션 관리'
        verbose_name_plural = '03. 파티션 관리'


class Category(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    name = models.CharField('이름', max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='상위 카테고리')
    order = models.PositiveSmallIntegerField('정렬 순서', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = '04. 카테고리 관리'
        verbose_name_plural = '04. 카테고리 관리'


class Post(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    is_notice = models.CharField('공지사항', max_length=1, choices=(('0', '일반'), ('1', '공지'), ('2', '전체공지')), default='0')
    partition = models.ForeignKey(Partition, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='파티션')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='카테고리')
    title = models.CharField('제목', max_length=255)
    content = models.TextField('내용', blank=True)
    is_hide_comment = models.BooleanField('댓글숨기기', default=False)
    hit = models.PositiveIntegerField('조회수', default=0)
    like = models.PositiveIntegerField('추천', default=0)
    dislike = models.PositiveIntegerField('비추천', default=0)
    blame = models.PositiveSmallIntegerField('신고', default=0)
    ip = models.GenericIPAddressField('아이피', null=True, blank=True)
    device = models.CharField('등록기기', max_length=10, null=True, blank=True)
    secret = models.BooleanField('비밀글', default=False)
    password = models.CharField('패스워드', max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='등록자')
    soft_delete = models.DateTimeField('휴지통', null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # number = models.PositiveIntegerField()
    # reply = models.CharField('댓글', max_length=10)
    # link_count = models.PositiveIntegerField()
    # receive_email = models.BooleanField()
    # html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        verbose_name = '05. 게시물 관리'
        verbose_name_plural = '05. 게시물 관리'


def get_image_filename(instance, filename):
    today = datetime.today().strftime('%Y-%m-%d')
    hash_value = hashlib.md5().hexdigest()
    return f"{today}_{hash_value}_{filename}"


class Images(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    image = models.ImageField(upload_to=get_image_filename, verbose_name='이미지')


class Files(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    file = models.FileField(upload_to=get_image_filename, verbose_name='파일')


class Links(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    link = models.URLField(verbose_name='링크')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='게시물')
    content = models.TextField('내용', default='')
    like = models.PositiveIntegerField('추천', default=0)
    dislike = models.PositiveIntegerField('비추천', default=0)
    blame = models.PositiveSmallIntegerField('신고', default=0)
    ip = models.GenericIPAddressField('아이피', null=True, blank=True)
    device = models.CharField('등록기기', max_length=10, null=True, blank=True)
    secret = models.BooleanField('비밀글', default=False)
    password = models.CharField('패스워드', max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='등록자')
    soft_delete = models.DateTimeField('휴지통', null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # number = models.PositiveIntegerField()
    # reply = models.CharField('댓글', max_length=10)
    # html_type = models.CharField('', choices=(('1', 'html'), ('2', 'text'), ('3', 'aa'), ('4', 'bb')))

    def __str__(self):
        return f"{self.post} -> {self.content}"

    class Meta:
        ordering = ['-id']
        verbose_name = '06. 댓글 관리'
        verbose_name_plural = '06. 댓글 관리'


class Tag(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    tag = models.CharField('태그', max_length=100)
    post = models.ManyToManyField(Post, blank=True, verbose_name='게시물')

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ['id']
        verbose_name = '07. 태그 관리'
        verbose_name_plural = '07. 태그 관리'

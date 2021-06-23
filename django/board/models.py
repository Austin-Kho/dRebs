import hashlib
from django.db import models
from datetime import datetime
from django.conf import settings
from tinymce.models import HTMLField


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


class Category(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    name = models.CharField('이름', max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='상위 카테고리')
    order = models.PositiveSmallIntegerField('정렬 순서', default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = '03. 카테고리 관리'
        verbose_name_plural = '03. 카테고리 관리'


class LawsuitCase(models.Model):
    project = models.ForeignKey('rebs_project.Project', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='프로젝트')
    sort = models.CharField('구분', max_length=1, choices=(('1', '민사'), ('2', '형사')))
    level = models.CharField('심급', max_length=1, choices=(('1', '1심'), ('2', '2심'), ('3', '3심')), null=True, blank=True)
    related_case = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='관련사건', help_text='본안사건인 경우 이전 심급 사건, 신청사건인 경우 관련 본안 사건 지정')
    case_number = models.CharField('사건번호(사건명)', max_length=50)
    plaintiff = models.CharField('원고(신청인)', max_length=20)
    defendant = models.CharField('피고(피신청인)', max_length=20)
    case_start_date = models.DateField('사건개시일', null=True, blank=True)
    summary = models.TextField('개요 및 경과', null=True, blank=True)
    register = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='등록자')
    created = models.DateTimeField('등록일시', auto_now_add=True)
    updated = models.DateTimeField('수정일시', auto_now=True)

    def __str__(self):
        return self.case_number

    class Meta:
        ordering = ['-case_start_date', '-id']
        verbose_name = '04. 소송사건 관리'
        verbose_name_plural = '04. 소송사건 관리'


class Post(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    is_notice = models.BooleanField('공지', default=False)
    project = models.ForeignKey('rebs_project.Project', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='프로젝트')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='카테고리')
    lawsuit = models.ForeignKey(LawsuitCase, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='사건번호')
    title = models.CharField('제목', max_length=255)
    execution_date = models.DateField('문서 시행일자', null=True, blank=True, help_text='문서 발신/수신/시행일자')
    content = HTMLField('내용', blank=True)
    is_hide_comment = models.BooleanField('댓글숨기기', default=False)
    hit = models.PositiveIntegerField('조회수', default=0)
    like = models.PositiveIntegerField('좋아요', default=0)
    dislike = models.PositiveIntegerField('싫어요', default=0)
    blame = models.PositiveSmallIntegerField('신고', default=0)
    ip = models.GenericIPAddressField('아이피', null=True, blank=True)
    device = models.CharField('등록기기', max_length=10, null=True, blank=True)
    secret = models.BooleanField('비밀글', default=False)
    password = models.CharField('패스워드', max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='등록자')
    soft_delete = models.DateTimeField('휴지통', null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        verbose_name = '05. 게시물 관리'
        verbose_name_plural = '05. 게시물 관리'


def get_image_filename(instance, filename):
    today = datetime.today().strftime('%y%m%d')
    hash_value = hashlib.blake2b(digest_size=3).hexdigest()
    return f"{today}_{hash_value}_{filename}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    image = models.ImageField(upload_to=get_image_filename, verbose_name='이미지')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return settings.MEDIA_URL


class Link(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    link = models.URLField(max_length=500, verbose_name='링크')

    def __str__(self):
        return self.link


class File(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None, verbose_name='게시물')
    file = models.FileField(upload_to=get_image_filename, verbose_name='파일')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return settings.MEDIA_URL


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

    def __str__(self):
        return f"{self.post} -> {self.content}"

    class Meta:
        ordering = ['-id']


class Tag(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판')
    tag = models.CharField('태그', max_length=100)
    post = models.ManyToManyField(Post, blank=True, verbose_name='게시물')

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ['id']
        verbose_name = '06. 태그 관리'
        verbose_name_plural = '06. 태그 관리'

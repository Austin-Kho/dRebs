from django.db import models
from django.conf import settings


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
        verbose_name = '소송 사건'
        verbose_name_plural = '소송 사건'

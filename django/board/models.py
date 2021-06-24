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
    sort = models.CharField('구분', max_length=1, choices=(('1', '민사'), ('2', '형사'), ('3', '행정'), ('4', '가사'), ('5', '신청/집행')))
    level = models.CharField('심급', max_length=1, choices=(('0', '신청/집행'), ('1', '1심'), ('2', '2심'), ('3', '3심')), null=True, blank=True)
    related_case = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='관련사건', help_text='본안사건인 경우 이전 심급 사건, 신청/집행 사건인 경우 관련 본안 사건 지정')
    CHOICES = (
        ('000100', '대법원'),
        ('000200', '서울고등법원'),
        ('000201', '서울고등법원(춘천재판부)'),
        ('000202', '서울고등법원(인천재판부)'),
        ('000600', '대전고등법원'),
        ('000601', '대전고등법원(청주재판부)'),
        ('000300', '대구고등법원'),
        ('000400', '부산고등법원'),
        ('000401', '부산고등법원(창원재판부)'),
        ('000402', '부산고등법원(울산재판부)'),
        ('000500', '광주고등법원'),
        ('000501', '광주고등법원(제주재판부)'),
        ('000502', '광주고등법원(전주재판부)'),
        ('000800', '수원고등법원'),
        ('000700', '특허법원'),
        ('000230', '서울가정법원'),
        ('000220', '서울행정법원'),
        ('000221', '서울회생법원'),
        ('', '------------'),
        ('000210', '서울중앙지방법원'),
        ('000211', '서울동부지방법원'),
        ('000212', '서울남부지방법원'),
        ('000213', '서울북부지방법원'),
        ('000215', '서울서부지방법원'),
        ('', '------------'),
        ('000214', '의정부지방법원'),
        ('214807', '고양지원'),
        ('214801', '파주시법원'),
        ('214802', '포천시법원'),
        ('214804', '남양주시법원'),
        ('214808', '동두천시법원'),
        ('214803', '가평군법원'),
        ('214805', '연천군법원'),
        ('214806', '철원군법원'),
        ('', '------------'),
        ('000240', '인천지방법원'),
        ('000241', '인천지방법원 부천지원'),
        ('240812', '김포시법원'),
        ('240811', '강화군법원'),
        ('000228', '인천가정법원'),
        ('000229', '인천가정법원 부천지원'),
        ('', '------------'),
        ('000250', '수원지방법원'),
        ('000251', '성남지원'),
        ('000252', '여주지원'),
        ('000253', '평택지원'),
        ('250826', '안산지원'),
        ('000254', '안양지원'),
        ('250823', '용인시법원'),
        ('250824', '오산시법원'),
        ('250825', '광명시법원'),
        ('250821', '안성시법원'),
        ('251827', '광주시법원'),
        ('252828', '양평군법원'),
        ('252829', '이천시법원'),
        ('000302', '수원가정법원'),
        ('000303', '수원가정법원 성남지원'),
        ('000304', '수원가정법원 여주지원'),
        ('000305', '수원가정법원 평택지원'),
        ('000322', '수원가정법원 안산지원'),
        ('000306', '수원가정법원 안양지원'),
        ('', '------------'),
        ('000260', '춘천지방법원'),
        ('000261', '강릉지원'),
        ('000262', '원주지원'),
        ('000263', '속초지원'),
        ('000264', '영월지원'),
        ('260842', '홍천군법원'),
        ('260843', '양구군법원'),
        ('261845', '삼척시법원'),
        ('261846', '동해시법원'),
        ('264851', '정선군법원'),
        ('264853', '평창군법원'),
        ('264852', '태백시법원'),
        ('262847', '횡성군법원'),
        ('260841', '인제군법원'),
        ('260844', '화천군법원'),
        ('263848', '고성군법원'),
        ('263849', '양양군법원'),
        ('', '------------'),
        ('000280', '대전지방법원'),
        ('000281', '대전지방법원 홍성지원'),
        ('000284', '대전지방법원 공주지원'),
        ('000282', '대전지방법원 논산지원'),
        ('000285', '대전지방법원 서산지원'),
        ('000283', '대전지방법원 천안지원'),
        ('280872', '금산군법원'),
        ('280871', '세종특별자치시법원'),
        ('281874', '보령시법원'),
        ('281873', '서천군법원'),
        ('281875', '예산군법원'),
        ('283877', '아산시법원'),
        ('285879', '태안군법원'),
        ('285881', '당진시법원'),
        ('282876', '부여군법원'),
        ('284878', '청양군법원'),
        ('000286', '대전가정법원'),
        ('000292', '대전가정법원 홍성지원'),
        ('000295', '대전가정법원 공주지원'),
        ('000293', '대전가정법원 논산지원'),
        ('000296', '대전가정법원 서산지원'),
        ('000294', '대전가정법원 천안지원'),
        ('', '------------'),
        ('000270', '청주지방법원'),
        ('000271', '충주지원'),
        ('000272', '제천지원'),
        ('000273', '영동지원'),
        ('270863', '진천군법원'),
        ('270861', '보은군법원'),
        ('272865', '단양군법원'),
        ('271864', '음성군법원'),
        ('273866', '옥천군법원'),
        ('270862', '괴산군법원'),
        ('', '------------'),
        ('000310', '대구지방법원'),
        ('000320', '대구지방법원 서부지원'),
        ('000311', '대구지방법원 안동지원'),
        ('000312', '대구지방법원 경주지원'),
        ('000317', '대구지방법원 포항지원'),
        ('000313', '대구지방법원 김천지원'),
        ('000314', '대구지방법원 상주지원'),
        ('000315', '대구지방법원 의성지원'),
        ('000316', '대구지방법원 영덕지원'),
        ('310895', '경산시법원'),
        ('310893', '칠곡군법원'),
        ('310891', '청도군법원'),
        ('310892', '영천시법원'),
        ('310894', '성주군법원'),
        ('310896', '고령군법원'),
        ('311897', '영주시법원'),
        ('311898', '봉화군법원'),
        ('313901', '구미시법원'),
        ('314903', '문경시법원'),
        ('314902', '예천군법원'),
        ('315904', '청송군법원'),
        ('315905', '군위군법원'),
        ('316906', '울진군법원'),
        ('316907', '영양군법원'),
        ('000318', '대구가정법원'),
        ('000399', '대구가정법원 안동지원'),
        ('000390', '대구가정법원 경주지원'),
        ('000395', '대구가정법원 포항지원'),
        ('000391', '대구가정법원 김천지원'),
        ('000392', '대구가정법원 상주지원'),
        ('000393', '대구가정법원 의성지원'),
        ('000394', '대구가정법원 영덕지원'),
        ('', '------------'),
        ('000410', '부산지방법원'),
        ('000412', '부산지방법원 동부지원'),
        ('000414', '부산지방법원 서부지원'),
        ('000413', '부산가정법원'),
        ('', '------------'),
        ('000411', '울산지방법원'),
        ('411911', '양산시법원'),
        ('000477', '울산가정법원'),
        ('', '------------'),
        ('000420', '창원지방법원'),
        ('000431', '마산지원'),
        ('000421', '진주지원'),
        ('000422', '통영지원'),
        ('000423', '밀양지원'),
        ('000424', '거창지원'),
        ('420922', '창원남부시법원'),
        ('420923', '김해시법원'),
        ('420921', '함안군법원'),
        ('420924', '의령군법원'),
        ('421927', '사천시법원'),
        ('421928', '남해군법원'),
        ('421926', '하동군법원'),
        ('422931', '거제시법원'),
        ('422932', '고성군법원(경)'),
        ('423933', '창녕군법원'),
        ('424934', '합천군법원'),
        ('424935', '함양군법원'),
        ('421929', '산청군법원'),
        ('', '------------'),
        ('000510', '광주지방법원'),
        ('000511', '광주지방법원 목포지원'),
        ('000512', '광주지방법원 장흥지원'),
        ('000513', '광주지방법원 순천지원'),
        ('000514', '광주지방법원 해남지원'),
        ('510946', '담양군법원'),
        ('511947', '함평군법원'),
        ('512951', '강진군법원'),
        ('513955', '구례군법원'),
        ('510942', '영광군법원'),
        ('510943', '나주시법원'),
        ('510944', '장성군법원'),
        ('510945', '화순군법원'),
        ('510941', '곡성군법원'),
        ('513956', '광양시법원'),
        ('513953', '고흥군법원'),
        ('513954', '여수시법원'),
        ('513952', '보성군법원'),
        ('511949', '무안군법원'),
        ('511948', '영암군법원'),
        ('514958', '완도군법원'),
        ('514959', '진도군법원'),
        ('000515', '광주가정법원'),
        ('000599', '광주가정법원 목포지원'),
        ('000590', '광주가정법원 장흥지원'),
        ('000591', '광주가정법원 순천지원'),
        ('000592', '광주가정법원 해남지원'),
        ('', '------------'),
        ('000520', '전주지방법원'),
        ('000521', '군산지원'),
        ('000522', '정읍지원'),
        ('000523', '남원지원'),
        ('520971', '진안군법원'),
        ('520972', '김제시법원'),
        ('520973', '무주군법원'),
        ('520974', '임실군법원'),
        ('521975', '익산시법원'),
        ('522976', '부안군법원'),
        ('522977', '고창군법원'),
        ('523978', '장수군법원'),
        ('523979', '순창군법원'),
        ('', '------------'),
        ('000530', '제주지방법원'),
        ('530991', '서귀포시법원'),
        ('', '------------'),
        ('000110', '법원행정처')
    )
    court = models.CharField('법원명', max_length=30, choices=CHOICES)
    case_number = models.CharField('사건번호', max_length=20)
    case_name = models.CharField('사건명', max_length=30, null=True, blank=True)
    plaintiff = models.CharField('원고(신청인)', max_length=20, null=True, blank=True)
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

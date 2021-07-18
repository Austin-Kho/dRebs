from account.models import User
from rest_framework import serializers

from books.models import Book, Subject
from rebs_company.models import Company, Department, Staff
from rebs.models import (AccountSubD1, AccountSubD2, AccountSubD3,
                         ProjectAccountD1, ProjectAccountD2, WiseSaying)
from rebs_project.models import (Project, UnitType, UnitFloorType,
                                 ContractUnit, UnitNumber, ProjectBudget,
                                 Site, SiteOwner, SiteOwnshipRelationship, SiteContract)
from rebs_contract.models import (OrderGroup, Contract, Contractor,
                                  ContractorAddress, ContractorContact, ContractorRelease)
from rebs_cash.models import (BankCode, CompanyBankAccount, ProjectBankAccount,
                              CashBook, ProjectCashBook, SalesPriceByGT,
                              InstallmentPaymentOrder, DownPayment, OverDueRule)
from rebs_notice.models import SalesBillIssue
from board.models import Group, Board, Category, LawsuitCase, Post, Image, Link, Comment, Tag


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'is_active', 'date_joined', 'is_staff')


class CompanyInDepartsSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:depart-detail')

    class Meta:
        model = Department
        fields = ('url', 'name')


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:company-detail')
    departments = CompanyInDepartsSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('pk', 'url', 'name', 'ceo', 'tax_number', 'org_number',
                  'business_cond', 'business_even', 'es_date', 'op_date', 'zipcode',
                  'address1', 'address2', 'address3', 'departments')


class StaffInDepartmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:staff-detail')

    class Meta:
        model = Staff
        fields = ('url', 'position', 'name')

class DepartmentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:depart-detail')
    company = serializers.SlugRelatedField(queryset=Company.objects.all(), slug_field='name')
    staffs = StaffInDepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ('pk', 'url', 'company', 'name', 'task', 'staffs')


class StaffSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:staff-detail')
    department = serializers.SlugRelatedField(queryset=Department.objects.all(), slug_field='name')
    gender = serializers.ChoiceField(choices=Staff.GENDER_CHOICES)
    gender_desc = serializers.CharField(source='get_gender_display', read_only=True)
    status = serializers.ChoiceField(choices=Staff.STATUS_CHOICES)
    status_desc = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Staff
        fields = ('pk', 'url', 'department', 'position', 'name', 'birth_date', 'gender', 'gender_desc',
                  'entered_date', 'personal_phone', 'email', 'status', 'status_desc')


class BookSubjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:subject-detail')

    class Meta:
        model = Subject
        fields = ('url', 'title')


class BookSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:book-detail")
    user = serializers.ReadOnlyField(source='user.username', required=False)

    class Meta:
        model = Book
        fields = ('url', 'pk', 'user', 'title', 'disclosure', 'author', 'translator', 'publisher', 'pub_date', 'description', 'created_at', 'updated_at')


class SubjectBookSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:book-detail')

    class Meta:
        model = Book
        fields = ('title', 'url')


class SubjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:subject-detail")
    user = serializers.ReadOnlyField(source='user.username', required=False)
    book = SubjectBookSerializer()

    class Meta:
        model = Subject
        fields = ('url', 'user', 'book', 'seq', 'title', 'level', 'content', 'created_at', 'updated_at')

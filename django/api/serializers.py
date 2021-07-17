from account.models import User
from rest_framework import serializers

from books.models import Book, Subject
from rebs.models import (AccountSubD1, AccountSubD2, AccountSubD3,
                         ProjectAccountD1, ProjectAccountD2, WiseSaying)
from rebs_company.models import Company, Department, Staff
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

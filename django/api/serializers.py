from rest_framework import serializers

from books.models import Book, Subject
from rebs.models import (AccountSubD1, AccountSubD2, AccountSubD3,
                         ProjectAccountD1, ProjectAccountD2, WiseSaying)
from rebs_company.models import Company, Department
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


class BookSerializer(serializers.ModelSerializer):
    subjects = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='api:subject-detail')
    url = serializers.HyperlinkedIdentityField(view_name="api:book-detail")

    class Meta:
        model = Book
        fields = ('url', 'pk', 'title', 'subjects', 'disclosure', 'author', 'translator', 'publisher', 'pub_date', 'description', 'created_at', 'updated_at')
        # fields = ('url', 'pk', 'title', 'disclosure', 'author', 'translator', 'publisher', 'pub_date', 'description', 'created_at', 'updated_at')


class SubjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:subject-detail")
    # We want to display the subject book's name instead of the id
    book = serializers.SlugRelatedField(queryset=Book.objects.all(), slug_field='title')

    class Meta:
        model = Subject
        fields = ('url', 'book', 'seq', 'title', 'level', 'content', 'created_at', 'updated_at')

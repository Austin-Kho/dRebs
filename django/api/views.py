from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework.reverse import reverse

from . serializers import *

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


class BookList(generics.ListCreateAPIView):
    name = 'book-list'
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'book-detail'
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class SubjectList(generics.ListCreateAPIView):
    name = 'subject-list'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'subject-detail'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

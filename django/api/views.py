from account.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse

from . permission import *
from . serializers import *

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


class ApiIndex(generics.GenericAPIView):
    name = 'api-index'

    def get(self, request, *args, **kwargs):
        api = 'api:'
        return Response({
            'users': reverse(api + UserList.name, request=request),
            'companies': reverse(api + CompanyList.name, request=request),
            'departments': reverse(api + DepartmentList.name, request=request),
            'staffs': reverse(api + StaffList.name, request=request),
            'books': reverse(api + BookList.name, request=request),
            'subjects': reverse(api + SubjectList.name, request=request),
        })


class UserList(generics.ListAPIView):
    name = 'user-list'
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    name = 'user-detail'
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CompanyList(generics.ListAPIView):
    name = 'company-list'
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsSuperUserOrReadOnly)


class CompanyDetail(generics.RetrieveAPIView):
    name = 'company-detail'
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsSuperUserOrReadOnly)


class DepartmentList(generics.ListCreateAPIView):
    name = 'depart-list'
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)


class DepartmentDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'depart-detail'
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)


class StaffList(generics.ListCreateAPIView):
    name = 'staff-list'
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)


class StaffDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'staff-detail'
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsStaffOrReadOnly)


class BookList(generics.ListCreateAPIView):
    name = 'book-list'
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'book-detail'
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class SubjectList(generics.ListCreateAPIView):
    name = 'subject-list'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubjectDetail(generics.RetrieveUpdateDestroyAPIView):
    name = 'subject-detail'
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)



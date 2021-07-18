"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . views import *


app_name = 'api'

urlpatterns = [
    path('', ApiIndex.as_view(), name=ApiIndex.name),
    path('company/', CompanyList.as_view(), name=CompanyList.name),
    path('company/<int:pk>/', CompanyDetail.as_view(), name=CompanyDetail.name),
    path('departments/', DepartmentList.as_view(), name=DepartmentList.name),
    path('departments/<int:pk>/', DepartmentDetail.as_view(), name=DepartmentDetail.name),
    path('staff/', StaffList.as_view(), name=StaffList.name),
    path('staff/<int:pk>/', StaffDetail.as_view(), name=StaffDetail.name),
    path('users/', UserList.as_view(), name=UserList.name),
    path('users/<int:pk>/', UserDetail.as_view(), name=UserDetail.name),
    path('books/', BookList.as_view(), name=BookList.name),
    path('books/<int:pk>/', BookDetail.as_view(), name=BookDetail.name),
    path('subjects/', SubjectList.as_view(), name=SubjectList.name),
    path('subjects/<int:pk>/', SubjectDetail.as_view(), name=SubjectDetail.name),
]

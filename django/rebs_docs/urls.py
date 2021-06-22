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
from .views import *

app_name = 'docs'

urlpatterns = [
    path('general/', CompanyGeneralDocsLV.as_view(), name='co.general_list'),
    path('general/<int:pk>/', CompanyGeneralDocsDV.as_view(), name='co.general_detail'),
    path('general/add/', CompanyGeneralDocsCV.as_view(), name='co.general_create'),
    path('general/update/<int:pk>/', CompanyGeneralDocsUV.as_view(), name='co.general_update'),
    path('general/delete/<int:pk>/', CompanyGeneralDocsDelete.as_view(), name='co.general_delete'),

    path('lawsuit/', CompanyLawsuitDocsLV.as_view(), name='co.lawsuit_list'),
    path('lawsuit/<int:pk>/', CompanyLawsuitDocsDV.as_view(), name='co.lawsuit_detail'),
    path('lawsuit/add/', CompanyLawsuitDocsCV.as_view(), name='co.lawsuit_create'),
    path('lawsuit/update/<int:pk>/', CompanyLawsuitDocsUV.as_view(), name='co.lawsuit_update'),
    path('lawsuit/delete/<int:pk>/', CompanyLawsuitDocsDelete.as_view(), name='co.lawsuit_delete'),

    path('project/general/', ProjectGeneralDocsLV.as_view(), name='pr.general_list'),
    path('project/general/<int:pk>/', ProjectGeneralDocsDV.as_view(), name='pr.general_detail'),
    path('project/general/add/', ProjectGeneralDocsCV.as_view(), name='pr.general_create'),
    path('project/general/update/<int:pk>/', ProjectGeneralDocsUV.as_view(), name='pr.general_update'),
    path('project/general/delete/<int:pk>/', ProjectGeneralDocsDelete.as_view(), name='pr.general_delete'),

    path('project/lawsuit/', ProjectLawsuitDocsLV.as_view(), name='pr.lawsuit_list'),
    path('project/lawsuit/<int:pk>/', ProjectLawsuitDocsDV.as_view(), name='pr.lawsuit_detail'),
    path('project/lawsuit/add/', ProjectLawsuitDocsCV.as_view(), name='pr.lawsuit_create'),
    path('project/lawsuit/update/<int:pk>/', ProjectLawsuitDocsUV.as_view(), name='pr.lawsuit_update'),
    path('project/lawsuit/delete/<int:pk>/', ProjectLawsuitDocsDelete.as_view(), name='pr.lawsuit_delete'),
]

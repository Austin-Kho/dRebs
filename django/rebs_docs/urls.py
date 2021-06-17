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
    path('lawsuit/', CompanyLawsuitDocsLV.as_view(), name='co.lawsuit_list'),
    path('project/general/', ProjectGeneralDocsLV.as_view(), name='pr.general_list'),
    path('project/general/<int:pk>/', ProjectGeneralDocsDV.as_view(), name='pr.general_detail'),
    path('project/lawsuit/', ProjectLawsuitDocsLV.as_view(), name='pr.lawsuit_list'),
]

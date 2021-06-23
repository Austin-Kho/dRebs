from django.contrib import admin
from import_export.admin import ImportExportMixin
from .models import LawsuitCase


class LawsuitCaseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('project', 'sort', 'level', 'related_case', 'case_number', 'plaintiff', 'defendant', 'case_start_date')
    list_display_links = ('case_number',)
    list_editable = ('project', 'sort', 'level', 'related_case', 'case_start_date',)
    list_filter = ('project', 'sort', 'level')
    search_fields = ('case_number', 'plaintiff', 'defendant')


admin.site.register(LawsuitCase, LawsuitCaseAdmin)

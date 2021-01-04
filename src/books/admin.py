from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget
from . models import Book, Subject, Images


class BooksAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'translator', 'publisher', 'pub_date')
    search_fields = ('title', 'author', 'translator', 'publisher')
    list_filter = ('pub_date',)
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }

class ImagesInline(admin.StackedInline):
    model = Images
    extra = 1

class SubjectAdmin(admin.ModelAdmin):
    inlines = (ImagesInline,)

admin.site.register(Book, BooksAdmin)
admin.site.register(Subject, SubjectAdmin)

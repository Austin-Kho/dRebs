from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget
from import_export.admin import ImportExportMixin
from . models import Group, Board, Category, Post, Comment, Tag


class GroupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'url', 'name', 'order')


class BoardAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


class PostAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


class CommentAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


class TagAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


admin.site.register(Group, GroupAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)

from django.contrib import admin
from import_export.admin import ImportExportMixin
from . models import Group, Board, Category, Post, Image, File, Link, Comment, Tag


class GroupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class BoardAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'group', 'name', 'order', 'search_able')
    list_display_links = ('name',)
    list_editable = ('group', 'order', 'search_able')
    search_fields = ('name',)
    list_filter = ('group',)
    inlines = (CategoryInline,)


class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'name', 'parent', 'order')
    list_display_links = ('name',)
    list_editable = ('board', 'parent', 'order')
    search_fields = ('name',)
    list_filter = ('board',)


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class FileInline(admin.TabularInline):
    model = File
    extra = 1

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class PostAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'is_notice', 'project', 'category', 'title', 'execution_date')
    list_display_links = ('title',)
    list_editable = ('board', 'is_notice', 'project', 'category', 'execution_date')
    search_fields = ('title', 'content')
    list_filter = ('board', 'is_notice', 'project', 'category')
    inlines = (ImageInline, FileInline, LinkInline)


class TagAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'tag')
    list_editable = ('tag',)
    search_fields = ('tag',)
    list_filter = ('board',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)

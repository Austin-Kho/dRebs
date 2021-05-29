from django.contrib import admin
from mdeditor.widgets import MDEditorWidget
from import_export.admin import ImportExportMixin
from . models import Group, Board, Category, Post, Comment, Tag


class GroupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)


# class PartitionInline(admin.TabularInline):
#     model = Partition
#     extra = 1


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


# class PartitionAdmin(ImportExportMixin, admin.ModelAdmin):
#     list_display = ('id', 'board', 'name', 'project', 'order')
#     list_display_links = ('name',)
#     list_editable = ('board', 'project', 'order')
#     search_fields = ('name',)
#     list_filter = ('board', 'project')


class CategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'name', 'parent', 'order')
    list_display_links = ('name',)
    list_editable = ('board', 'parent', 'order')
    search_fields = ('name',)
    list_filter = ('board',)


class PostAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'is_notice', 'project', 'category', 'title', 'user')
    list_display_links = ('title',)
    list_editable = ('board', 'is_notice', 'project', 'category')
    search_fields = ('title', 'content')
    list_filter = ('board', 'is_notice', 'category')


class CommentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'post', 'content', 'user')
    list_display_links = ('post', 'content',)
    search_fields = ('content', 'user')


class TagAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'board', 'tag')
    list_editable = ('tag',)
    search_fields = ('tag',)
    list_filter = ('board',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Board, BoardAdmin)
# admin.site.register(Partition, PartitionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)

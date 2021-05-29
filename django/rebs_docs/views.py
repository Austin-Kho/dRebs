from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, TemplateView

from board.models import Board, Category, Post
from rebs_project.models import Project


class CompanyGeneralDocs(LoginRequiredMixin, ListView):

    template_name = 'rebs_docs/project_general_docs_board.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_board(self):
        return Board.objects.first()

    def get_post_list(self):
        posts = Post.objects.filter(board=self.get_board())
        return posts

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocs, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True, project=None)
        return context

    def get_queryset(self):
        project = self.request.GET.get('project')
        category = self.request.GET.get('category')
        objects = self.get_post_list().filter(is_notice=False)
        if project:
            if project == 'co':
                objects = objects.filter(project=None)
            else:
                objects = objects.filter(partition__project=project)
        if category:
            objects = objects.filter(category=category)
        return objects


class CompanyLawsuitDocs(LoginRequiredMixin, ListView):

    template_name = 'rebs_docs/project_general_docs_board.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_board(self):
        return Board.objects.get(pk=2)

    def get_post_list(self):
        posts = Post.objects.filter(board=self.get_board())
        return posts

    def get_context_data(self, **kwargs):
        context = super(CompanyLawsuitDocs, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True, project=None)
        return context

    def get_queryset(self):
        project = self.request.GET.get('project')
        category = self.request.GET.get('category')
        objects = self.get_post_list().filter(is_notice=False)
        if project:
            if project == 'co':
                objects = objects.filter(project=None)
            else:
                objects = objects.filter(project=project)
        if category:
            objects = objects.filter(category=category)
        return objects


class ProjectGeneralDocs(LoginRequiredMixin, ListView):

    template_name = 'rebs_docs/project_general_docs_board.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_board(self):
       return Board.objects.first()

    def get_post_list(self):
        return Post.objects.filter(board=self.get_board(), project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocs, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] =self.get_post_list().filter(is_notice=True)
        return context

    def get_queryset(self):
        object = self.get_post_list().filter(is_notice=False)
        if self.request.GET.get('category'):
            object = object.filter(category=self.request.GET.get('category'))
        return object


class ProjectLawsuitDocs(LoginRequiredMixin, ListView):
    template_name = 'rebs_docs/project_general_docs_board.html'

    def get_paginate_by(self, queryset):
        return self.request.GET.get('limit') if self.request.GET.get('limit') else 15

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_board(self):
        return Board.objects.get(pk=2)

    def get_post_list(self):
        return Post.objects.filter(board=self.get_board(), project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocs, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True)
        return context

    def get_queryset(self):
        object = self.get_post_list().filter(is_notice=False)
        if self.request.GET.get('category'):
            object = object.filter(category=self.request.GET.get('category'))
        return object

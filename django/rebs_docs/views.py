import math
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, TemplateView

from board.models import Board, Category, Post
from rebs_project.models import Project


class CompanyGeneralDocs(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'rebs_docs/project_general_docs_board.html'
    paginate_by = 15

    def get_board(self):
        return Board.objects.first()

    def get_post_list(self):
        posts = self.model.objects.filter(board=self.get_board())
        return posts

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocs, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True, project=None)
        post_num = self.get_queryset().count() # 총 게시물 수
        page = self.request.GET.get('page')    # 현재 페이지
        page_num = int(page) if page else 1    # 현재 페이지 수
        first_page_mod = self.get_queryset().count() % self.paginate_by # 첫 페이지 나머지
        total_page = math.ceil(post_num/self.paginate_by) # 총 페이지 수
        add_num = (total_page-page_num)*self.paginate_by-(self.paginate_by-first_page_mod)
        context['add_num'] = add_num if add_num >=0 else 0
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


class CompanyLawsuitDocs(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'rebs_docs/project_general_docs_board.html'
    paginate_by = 15

    def get_board(self):
        return Board.objects.get(pk=2)

    def get_post_list(self):
        posts = self.model.objects.filter(board=self.get_board())
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
    model = Post
    template_name = 'rebs_docs/project_general_docs_board.html'
    paginate_by = 15

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
        return self.model.objects.filter(board=self.get_board(), project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocs, self).get_context_data(**kwargs)
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
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
    model = Post
    template_name = 'rebs_docs/project_general_docs_board.html'
    paginate_by = 15

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
        return self.model.objects.filter(board=self.get_board(), project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocs, self).get_context_data(**kwargs)
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
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

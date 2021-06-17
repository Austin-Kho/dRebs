import math
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView

from board.models import Board, Category, Post
from rebs_project.models import Project


class CompanyGeneralDocsLV(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'board/board_list.html'
    paginate_by = 15

    def get_board(self):
        return Board.objects.first()

    def get_post_list(self):
        posts = self.model.objects.filter(board=self.get_board())
        return posts

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocsLV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True, project=None)
        post_num = self.get_queryset().count() # 총 게시물 수
        page = self.request.GET.get('page')    # 현재 페이지
        page_num = int(page) if page else 1    # 현재 페이지 수
        first_page_mod = post_num % self.paginate_by # 첫 페이지 나머지
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


class CompanyGeneralDocsDV(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'board/board_view.html'
    paginate_by = 15

    def get_object(self):
        post = super().get_object()
        post.hit += 1
        post.save()
        return post

    def get_posts(self):
        return self.model.objects.filter(board=Board.objects.first())

    def get_prev(self):
        instance = self.get_posts().filter(id__lt=self.object.id).order_by('-id',).first()
        return reverse_lazy('rebs:docs:co.general_detail', args=[instance.id]) if instance else None

    def get_next(self):
        instance = self.get_posts().filter(id__gt=self.object.id).order_by('id',).first()
        return reverse_lazy('rebs:docs:co.general_detail', args=[instance.id]) if instance else None

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocsDV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.first()
        context['prev'] = self.get_prev() if self.get_prev() else ''
        context['next'] = self.get_next() if self.get_next() else ''
        return context


class CompanyGeneralDocsCV(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('__all__')


class CompanyLawsuitDocsLV(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'board/board_list.html'
    paginate_by = 15

    def get_board(self):
        return Board.objects.get(pk=2)

    def get_post_list(self):
        posts = self.model.objects.filter(board=self.get_board())
        return posts

    def get_context_data(self, **kwargs):
        context = super(CompanyLawsuitDocsLV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True, project=None)
        post_num = self.get_queryset().count()  # 총 게시물 수
        page = self.request.GET.get('page')  # 현재 페이지
        page_num = int(page) if page else 1  # 현재 페이지 수
        first_page_mod = self.get_queryset().count() % self.paginate_by  # 첫 페이지 나머지
        total_page = math.ceil(post_num / self.paginate_by)  # 총 페이지 수
        add_num = (total_page - page_num) * self.paginate_by - (self.paginate_by - first_page_mod)
        context['add_num'] = add_num if add_num >= 0 else 0
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


class ProjectGeneralDocsLV(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'board/board_list.html'
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
        return self.model.objects.filter(board=self.get_board(), project__isnull=False, project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocsLV, self).get_context_data(**kwargs)
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] =self.get_post_list().filter(is_notice=True)
        post_num = self.get_queryset().count()  # 총 게시물 수
        page = self.request.GET.get('page')  # 현재 페이지
        page_num = int(page) if page else 1  # 현재 페이지 수
        first_page_mod = self.get_queryset().count() % self.paginate_by  # 첫 페이지 나머지
        total_page = math.ceil(post_num / self.paginate_by)  # 총 페이지 수
        add_num = (total_page - page_num) * self.paginate_by - (self.paginate_by - first_page_mod)
        context['add_num'] = add_num if add_num >= 0 else 0
        return context

    def get_queryset(self):
        object = self.get_post_list().filter(is_notice=False)
        if self.request.GET.get('category'):
            object = object.filter(category=self.request.GET.get('category'))
        return object


class ProjectGeneralDocsDV(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'board/board_view.html'
    paginate_by = 15

    def get_object(self):
        post = super().get_object()
        post.hit += 1
        post.save()
        return post

    def get_project(self):
        return Project.objects.get(pk=self.object.project.pk)

    def get_posts(self):
        return self.model.objects.filter(board=Board.objects.first(),
                                         project__isnull=False,
                                         project=self.get_project())

    def get_prev(self):
        instance = self.get_posts().filter(id__lt=self.object.id).order_by('-id',).first()
        return reverse_lazy('rebs:docs:pr.general_detail', args=[instance.id]) if instance else None

    def get_next(self):
        instance = self.get_posts().filter(id__gt=self.object.id).order_by('id',).first()
        return reverse_lazy('rebs:docs:pr.general_detail', args=[instance.id]) if instance else None

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocsDV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.first()
        context['project_list'] = Project.objects.filter(pk=self.object.project.pk)
        context['this_project'] = self.get_project()
        context['prev'] = self.get_prev() if self.get_prev() else ''
        context['next'] = self.get_next() if self.get_next() else ''
        return context


class ProjectLawsuitDocsLV(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'board/board_list.html'
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
        return self.model.objects.filter(board=self.get_board(), project__isnull=False, project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocsLV, self).get_context_data(**kwargs)
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['this_board'] = self.get_board()
        context['categories'] = Category.objects.filter(board=self.get_board()).order_by('order', 'id')
        context['notices'] = self.get_post_list().filter(is_notice=True)
        post_num = self.get_queryset().count()  # 총 게시물 수
        page = self.request.GET.get('page')  # 현재 페이지
        page_num = int(page) if page else 1  # 현재 페이지 수
        first_page_mod = self.get_queryset().count() % self.paginate_by  # 첫 페이지 나머지
        total_page = math.ceil(post_num / self.paginate_by)  # 총 페이지 수
        add_num = (total_page - page_num) * self.paginate_by - (self.paginate_by - first_page_mod)
        context['add_num'] = add_num if add_num >= 0 else 0
        return context

    def get_queryset(self):
        object = self.get_post_list().filter(is_notice=False)
        if self.request.GET.get('category'):
            object = object.filter(category=self.request.GET.get('category'))
        return object

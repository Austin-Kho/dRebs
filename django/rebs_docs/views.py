import math
from django import forms
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView

from board.models import Board, Category, Post, File, Link
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


class CompanyGeneralDocsCV(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    LinkInlineFormSet = forms.models.inlineformset_factory(Post, Link, fields=['link'], extra=1)
    FileInlineFormSet = forms.models.inlineformset_factory(Post, File, fields=['file'], extra=1)
    success_message = "새 게시물이 등록되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:co.general_detail', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocsCV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.first()
        context['link_formset'] = self.LinkInlineFormSet(queryset=Link.objects.none(),)
        context['file_formset'] = self.FileInlineFormSet(queryset=File.objects.none(),)
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.first()
        form.instance.user = self.request.user

        link_formset = self.LinkInlineFormSet(self.request.POST,)
        file_formset = self.FileInlineFormSet(self.request.POST, self.request.FILES)

        with transaction.atomic():
            self.object = form.save()

            if link_formset.is_valid():
                link_formset.instance = self.object
                link_formset.save()

            if file_formset.is_valid():
                file_formset.instance = self.object
                file_formset.save()

        return super(CompanyGeneralDocsCV, self).form_valid(form)


class CompanyGeneralDocsUV(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    success_message = "수정한 내용이 저장되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:co.general_detail', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(CompanyGeneralDocsUV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.first()
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.first()
        form.instance.user = self.request.user
        return super(CompanyGeneralDocsUV, self).form_valid(form)


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


class CompanyLawsuitDocsDV(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'board/board_view.html'

    def get_object(self):
        post = super().get_object()
        post.hit += 1
        post.save()
        return post

    def get_post_list(self):
        return self.model.objects.filter(board=Board.objects.get(id=2))

    def get_prev(self):
        instance = self.get_post_list().filter(id__lt=self.object.id).order_by('-id',).first()
        return reverse_lazy('rebs:docs:co.lawsuit_detail', args=[instance.id]) if instance else None

    def get_next(self):
        instance = self.get_post_list().filter(id__gt=self.object.id).order_by('id',).first()
        return reverse_lazy('rebs:docs:co.lawsuit_detail', args=[instance.id]) if instance else None

    def get_context_data(self, **kwargs):
        context = super(CompanyLawsuitDocsDV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.get(pk=2)
        context['prev'] = self.get_prev() if self.get_prev() else ''
        context['next'] = self.get_next() if self.get_next() else ''
        return context


class CompanyLawsuitDocsCV(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    LinkInlineFormSet = forms.models.inlineformset_factory(Post, Link, fields=['link'], extra=1)
    FileInlineFormSet = forms.models.inlineformset_factory(Post, File, fields=['file'], extra=1)
    success_message = "새 게시물이 등록되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:co.lawsuit_detail', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(CompanyLawsuitDocsCV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.get(pk=2)
        context['link_formset'] = self.LinkInlineFormSet(queryset=Link.objects.none(), )
        context['file_formset'] = self.FileInlineFormSet(queryset=File.objects.none(), )
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.get(pk=2)
        form.instance.user = self.request.user

        link_formset = self.LinkInlineFormSet(self.request.POST, )
        file_formset = self.FileInlineFormSet(self.request.POST, self.request.FILES)

        with transaction.atomic():
            self.object = form.save()

            if link_formset.is_valid():
                link_formset.instance = self.object
                link_formset.save()

            if file_formset.is_valid():
                file_formset.instance = self.object
                file_formset.save()

        return super(CompanyLawsuitDocsCV, self).form_valid(form)


class CompanyLawsuitDocsUV(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    success_message = "수정한 내용이 저장되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:co.general_detail', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super(CompanyLawsuitDocsUV, self).get_context_data(**kwargs)
        context['co'] = True
        context['this_board'] = Board.objects.get(pk=2)
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.get(pk=2)
        form.instance.user = self.request.user
        return super(CompanyLawsuitDocsUV, self).form_valid(form)


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


class ProjectGeneralDocsCV(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    LinkInlineFormSet = forms.models.inlineformset_factory(Post, Link, fields=['link'], extra=1)
    FileInlineFormSet = forms.models.inlineformset_factory(Post, File, fields=['file'], extra=1)
    success_message = "새 게시물이 등록되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:pr.general_detail', args=(self.object.id,))

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocsCV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.first()
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['link_formset'] = self.LinkInlineFormSet(queryset=Link.objects.none(), )
        context['file_formset'] = self.FileInlineFormSet(queryset=File.objects.none(), )
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.first()
        form.instance.project = self.get_project()
        form.instance.user = self.request.user

        link_formset = self.LinkInlineFormSet(self.request.POST, )
        file_formset = self.FileInlineFormSet(self.request.POST, self.request.FILES)

        with transaction.atomic():
            self.object = form.save()

            if link_formset.is_valid():
                link_formset.instance = self.object
                link_formset.save()

            if file_formset.is_valid():
                file_formset.instance = self.object
                file_formset.save()

        return super(ProjectGeneralDocsCV, self).form_valid(form)


class ProjectGeneralDocsUV(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    success_message = "수정한 내용이 저장되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:pr.general_detail', args=(self.object.id,))

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocsUV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.first()
        context['project_list'] = Project.objects.filter(pk=self.object.project.pk)
        context['this_project'] = self.get_project()
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.first()
        form.instance.project = self.get_project()
        form.instance.user = self.request.user
        return super(ProjectGeneralDocsUV, self).form_valid(form)


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


class ProjectLawsuitDocsDV(LoginRequiredMixin, DetailView):
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
        return self.model.objects.filter(board=Board.objects.get(id=2),
                                         project__isnull=False,
                                         project=self.get_project())

    def get_prev(self):
        instance = self.get_posts().filter(id__lt=self.object.id).order_by('-id', ).first()
        return reverse_lazy('rebs:docs:pr.lawsuit_detail', args=[instance.id]) if instance else None

    def get_next(self):
        instance = self.get_posts().filter(id__gt=self.object.id).order_by('id', ).first()
        return reverse_lazy('rebs:docs:pr.lawsuit_detail', args=[instance.id]) if instance else None

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocsDV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.get(id=2)
        context['project_list'] = Project.objects.filter(pk=self.object.project.pk)
        context['this_project'] = self.get_project()
        context['prev'] = self.get_prev() if self.get_prev() else ''
        context['next'] = self.get_next() if self.get_next() else ''
        return context


class ProjectLawsuitDocsCV(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    LinkInlineFormSet = forms.models.inlineformset_factory(Post, Link, fields=['link'], extra=1)
    FileInlineFormSet = forms.models.inlineformset_factory(Post, File, fields=['file'], extra=1)
    success_message = "새 게시물이 등록되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:pr.lawsuit_detail', args=(self.object.id,))

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocsCV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.get(id=2)
        user = self.request.user
        context['project_list'] = Project.objects.all() if user.is_superuser else user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['link_formset'] = self.LinkInlineFormSet(queryset=Link.objects.none(), )
        context['file_formset'] = self.FileInlineFormSet(queryset=File.objects.none(), )
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.get(id=2)
        form.instance.project = self.get_project()
        form.instance.user = self.request.user

        link_formset = self.LinkInlineFormSet(self.request.POST, )
        file_formset = self.FileInlineFormSet(self.request.POST, self.request.FILES)

        with transaction.atomic():
            self.object = form.save()

            if link_formset.is_valid():
                link_formset.instance = self.object
                link_formset.save()

            if file_formset.is_valid():
                file_formset.instance = self.object
                file_formset.save()

        return super(ProjectLawsuitDocsCV, self).form_valid(form)


class ProjectLawsuitDocsUV(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['is_notice', 'category', 'title', 'execution_date', 'content']
    success_message = "수정한 내용이 저장되었습니다."

    def get_success_url(self):
        return reverse_lazy('rebs:docs:pr.general_detail', args=(self.object.id,))

    def get_project(self):
        try:
            project = self.request.user.staffauth.assigned_project
        except:
            project = Project.objects.first()
        gp = self.request.GET.get('project')
        project = Project.objects.get(pk=gp) if gp else project
        return project

    def get_context_data(self, **kwargs):
        context = super(ProjectLawsuitDocsUV, self).get_context_data(**kwargs)
        context['this_board'] = Board.objects.get(id=2)
        context['project_list'] = Project.objects.filter(pk=self.object.project.pk)
        context['this_project'] = self.get_project()
        return context

    def form_valid(self, form):
        form.instance.board = Board.objects.get(id=2)
        form.instance.project = self.get_project()
        form.instance.user = self.request.user
        return super(ProjectLawsuitDocsUV, self).form_valid(form)

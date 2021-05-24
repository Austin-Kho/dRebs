from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, TemplateView

from board.models import Board, Partition, Category, Post
from rebs_project.models import Project


class CompanyGeneralDocs(LoginRequiredMixin, ListView):
    pass


class CompanyLawsuitDocs(LoginRequiredMixin, ListView):
    pass


class ProjectGeneralDocs(LoginRequiredMixin, ListView):

    template_name = 'rebs_docs/project_docs_board.html'
    model = Post

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

    def get_partition(self):
        return Partition.objects.get(board=self.get_board(), project=self.get_project())

    def get_context_data(self, **kwargs):
        context = super(ProjectGeneralDocs, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        context['this_board'] = self.get_board()
        # context['notices'] = self.get_queryset().object.
        return context

    def get_queryset(self):
        base_data = Post.objects.filter(board=self.get_board(), partition=self.get_partition())
        object = base_data

        return object


class ProjectLawsuitDocs(LoginRequiredMixin, ListView):
    pass

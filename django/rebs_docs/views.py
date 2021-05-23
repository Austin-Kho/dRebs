from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView, TemplateView

from board.models import Post
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

    def get_context_data(self, **kwargs):
        context = super(ProjectDocsBoard, self).get_context_data(**kwargs)
        context['project_list'] = self.request.user.staffauth.allowed_projects.all()
        context['this_project'] = self.get_project()
        return context


class ProjectLawsuitDocs(LoginRequiredMixin, ListView):
    pass

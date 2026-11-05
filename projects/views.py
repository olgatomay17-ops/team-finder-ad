from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from .models import Project, ProjectMembership
from .forms import ProjectForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'page_obj'
    paginate_by = 12


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'
    pk_url_kwarg = 'pk'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class FavoriteProjectView(LoginRequiredMixin, ListView):
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return self.request.user.favorites.all()


@login_required
@require_POST
@csrf_exempt
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user

    if project in user.favorites.all():
        user.favorites.remove(project)
        is_favorite = False
    else:
        user.favorites.add(project)
        is_favorite = True

    return JsonResponse({'status': 'ok', 'is_favorite': is_favorite})


@login_required
@require_POST
@csrf_exempt
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Вы не автором'}, status=403)
    project.status = 'closed'
    project.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
@csrf_exempt
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status == 'closed':
        return JsonResponse({'status': 'error', 'message': 'Проект закрыт'})
    if project.owner == request.user:
        return JsonResponse({'status': 'error', 'message': 'Вы автор'}, status=400)

    membership = ProjectMembership.objects.filter(
        user=request.user, project=project
    ).first()

    if membership:
        membership.delete()
        is_participant = False
    else:
        ProjectMembership.objects.create(user=request.user, project=project)
        is_participant = True

    return JsonResponse({
        'status': 'ok',
        'participant': is_participant
    })

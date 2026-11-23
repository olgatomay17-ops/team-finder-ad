from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .models import PROJECT_STATUS_CLOSED, Project

PROJECTS_PER_PAGE = 12


def get_project_or_error(pk):
    project = Project.objects.filter(pk=pk).first()

    if project is None:
        return None, JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    return project, None


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PROJECTS_PER_PAGE


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"
    pk_url_kwarg = "pk"


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


class FavoriteProjectView(LoginRequiredMixin, ListView):
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"

    def get_queryset(self):
        return self.request.user.favorites.all()


@login_required
@require_POST
def toggle_favorite(request, pk):
    project, error_response = get_project_or_error(pk)

    if error_response:
        return error_response

    user = request.user
    is_favorite = user.favorites.filter(pk=project.pk).exists()

    if is_favorite:
        user.favorites.remove(project)
    else:
        user.favorites.add(project)

    return JsonResponse({"status": "ok", "is_favorite": not is_favorite})


@login_required
@require_POST
def complete_project(request, pk):
    project, error_response = get_project_or_error(pk)

    if error_response:
        return error_response

    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Вы не автор."},
            status=HTTPStatus.FORBIDDEN,
        )

    project.status = PROJECT_STATUS_CLOSED
    project.save()

    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def toggle_participate(request, pk):
    project, error_response = get_project_or_error(pk)

    if error_response:
        return error_response

    if project.status == PROJECT_STATUS_CLOSED:
        return JsonResponse(
            {"status": "error", "message": "Проект закрыт"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if project.owner == request.user:
        return JsonResponse(
            {"status": "error", "message": "Нельзя вступить в свой проект"},
            status=HTTPStatus.BAD_REQUEST,
        )

    membership = project.membership.filter(user=request.user).first()
    is_participant = membership is not None

    if membership:
        membership.delete()
    else:
        project.membership.create(user=request.user)

    return JsonResponse({"status": "ok", "participant": not is_participant})

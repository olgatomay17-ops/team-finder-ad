from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from .forms import UserLoginForm, UserPasswordChangeForm, UserProfileForm, UserRegistrationForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


class CustomLoginView(LoginView):
    authentication_form = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        filter_type = self.request.GET.get('filter')

        if not self.request.user.is_authenticated:
            return qs

        user = self.request.user

        if filter_type == 'owners-of-favorite-projects':
            qs = qs.filter(
                owned_projects__in=user.favorites.all()
            ).distinct()
        elif filter_type == 'owners-of-participating-projects':
            qs = qs.filter(
                owned_projects__participants=user
            ).distinct()
        elif filter_type == 'interested-in-my-projects':
            qs = qs.filter(
                favorites__in=user.owned_projects.all()
            ).distinct()
        elif filter_type == 'participants-of-my-projects':
            qs = qs.filter(
                participating_projects__in=user.owned_projects.all()
            ).distinct()

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_filter = self.request.GET.get('filter')
        context['active_filter'] = active_filter
        context['query_prefix'] = (
            f'filter={active_filter}&' if active_filter else ''
        )
        return context


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owned_projects'] = self.object.owned_projects.all().distinct()
        return context


class UserUdpateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'
    context_object_name = 'user'
    pk_url_kwarg = 'pk'

    def test_func(self):
        return self.request.user.pk == self.kwargs['pk']

    def get_success_url(self):
        return reverse_lazy('users:detail', kwargs={'pk': self.object.pk})


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    form_class = UserPasswordChangeForm

    def get_success_url(self):
        return reverse_lazy(
            'users:detail', kwargs={'pk': self.request.user.pk}
        )


def get_profile_redirect(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    return redirect('users:edit', pk=request.user.pk)

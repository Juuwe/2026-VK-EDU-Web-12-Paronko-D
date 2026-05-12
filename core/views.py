from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.generic import FormView, CreateView, UpdateView, DetailView
from django.urls import reverse, reverse_lazy
from .forms import LoginForm, SignupForm, SettingsForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from .models import Profile

PROFILE = {"rep": 40, "answers": 23, "views": "115k", "questions": 30,
            "tags": [{"name": f'tag{i}', "count": 3} for i in range(5)]}

class LoginView(FormView):
    form_class = LoginForm
    template_name = 'core/login.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        login(request=self.request, user=form.get_user())

        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)

        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next')

        is_safe = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )

        if next_url and is_safe:
            return next_url

        return reverse('index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'core/profile.html'

    def get_object(self, queryset=None):
        return Profile.objects.get_profile_stat(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_tags'] = Profile.objects.get_top_tags(self.request.user)
        return context

class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('login')

class SettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = SettingsForm
    template_name = 'core/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        profile = self.request.user.profile

        initial['nickname'] = profile.nickname
        initial['avatar'] = profile.avatar

        return initial

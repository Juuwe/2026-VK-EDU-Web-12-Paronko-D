from django.shortcuts import render

from .forms import LoginForm, SignupForm, SettingsForm

PROFILE = {"rep": 40, "answers": 23, "views": "115k", "questions": 30,
            "tags": [{"name": f'tag{i}', "count": 3} for i in range(5)]}

def login(request):
    login_form = LoginForm()
    context = {'form': login_form}
    return render(request, 'core/login.html', context)

def signup(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, request.FILES)
        if signup_form.is_valid():
            pass
    else:
        signup_form = SignupForm()

    context = {'form': signup_form}
    return render(request, 'core/signup.html', context)

def profile(request):
    context = {"profile": PROFILE, "top_tags": PROFILE["tags"]}
    return render(request, 'core/profile.html', context)

def settings(request):
    if request.method == 'POST':
        settings_form = SettingsForm(request.POST, request.FILES)
        if settings_form.is_valid():
            pass
    else:
        settings_form = SettingsForm(initial={'login': 'mocklogin', 'email': 'mock_email@mail.ru', 'nickname': 'mock_nick'})

    context = {'form': settings_form}

    return render(request, 'core/settings.html', context)

from django.shortcuts import render

def login(request):
    return render(request, 'core/login.html')

def signup(request):
    return render(request, 'core/signup.html')

def profile(request):
    return render(request, 'core/profile.html')

def settings(request):
    return render(request, 'core/settings.html')

from django.shortcuts import render

PROFILE = {"rep": 40, "answers": 23, "views": "115k", "questions": 30,
            "tags": [{"name": f'tag{i}', "count": 3} for i in range(5)]}

def login(request):
    return render(request, 'core/login.html')

def signup(request):
    return render(request, 'core/signup.html')

def profile(request):
    context = {"profile": PROFILE, "top_tags": PROFILE["tags"]}
    return render(request, 'core/profile.html', context)

def settings(request):
    return render(request, 'core/settings.html')

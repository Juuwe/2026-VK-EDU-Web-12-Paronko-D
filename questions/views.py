from django.shortcuts import render

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from random import randint

QUESTIONS = [
    {"id": i, "title": f'TITLE{i}', "text": f'TEXT{i}',
     "total_likes": randint(0, 20), "total_answers": randint(0, 20),
     "tags": [f'tag:{j}' for j in range(randint(5, 10), randint(11, 15))],
     "time": f'{randint(20, 30)}.0{randint(3, 4)}.2026'
    }
    for i in range(50)
]

ANSWERS = [
    {"id": i, "question_id": randint(0, 49),
     "author_nickname": f'author{i}', "text": f'text{i}', "total_likes": randint(0, 20),
     "checkbox_value": randint(0, 1), "time": f'{randint(20, 30)}.0{randint(3, 4)}.2026'
    }

    for i in range(10)
]

def paginate(queryset, request, per_page=20):
    page_number = request.GET.get('page', 1)

    paginator = Paginator(queryset, per_page)

    try:
        cur_page = paginator.page(page_number)
    except PageNotAnInteger:
        cur_page = paginator.page(1)
    except EmptyPage:
        cur_page = paginator.page(paginator.num_pages)

    return cur_page

def get_page_context(queryset, request):
    page_obj = paginate(queryset, request)
    page_range = page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

    return {'page_obj': page_obj, 'page_range': page_range}

def index(request):
    questions = QUESTIONS
    return render(request, 'questions/index.html', get_page_context(questions, request))

def hot(request):
    questions = QUESTIONS[::-1]
    return render(request, 'questions/hot.html', get_page_context(questions, request))

def tag(request, tag_name):
    questions = QUESTIONS[5:10]

    context = {'tag_name': tag_name}
    context.update(get_page_context(questions, request))

    return render(request, 'questions/tag.html', context)

def question(request, question_id):
    answers = ANSWERS

    context = {"question": QUESTIONS[question_id]}
    context.update(get_page_context(answers, request))

    return render(request, 'questions/question.html', context)

def ask(request):
    return render(request, 'questions/ask.html')

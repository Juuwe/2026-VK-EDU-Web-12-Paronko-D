from django.shortcuts import render

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import View, DetailView

from .models import Question

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

class BaseQuestionListView(View):
    template_name = None

    def get_queryset(self):
        return Question.objects.select_related('author').prefetch_related('tags').all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page_obj = paginate(queryset, request, per_page=20)
        context = {'questions': page_obj.object_list, 'page_obj': page_obj}
        context.update(self.get_extra_context())

        return render(request, self.template_name, context)

    def get_extra_context(self):
        return {}

class IndexView(BaseQuestionListView):
    template_name = 'questions/index.html'

class HotView(BaseQuestionListView):
    template_name = 'questions/hot.html'

    def get_queryset(self):
        return Question.objects.hot().select_related('author').prefetch_related('tags')

class ByTagView(BaseQuestionListView):
    template_name = 'questions/tag.html'

    def get_queryset(self):
        return Question.objects.tag(self.kwargs['tag_name']).select_related('author').prefetch_related('tags')

    def get_extra_context(self):
        return {'tag_name': self.kwargs['tag_name']}


class DetailQuestionView(DetailView):
    model = Question
    template_name = 'questions/question.html'

    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answers_queryset = self.object.answers.all().select_related('author')
        page_obj = paginate(answers_queryset, self.request, per_page=5)

        context['page_obj'] = page_obj

        context.update({
            'page_obj': page_obj,
            'answers': page_obj.object_list
        })

        return context

def ask(request):
    return render(request, 'questions/ask.html')

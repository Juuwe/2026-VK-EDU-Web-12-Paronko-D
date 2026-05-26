from django.shortcuts import redirect, render

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import View, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Question
from .forms import AskForm, AnswerForm
import math

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
    per_page = 5

    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        answers_queryset = self.object.answers.best().select_related('author')
        page_obj = paginate(answers_queryset, self.request, per_page=self.per_page)
        context['page_obj'] = page_obj

        context.update({
            'page_obj': page_obj,
            'answers': page_obj.object_list
        })

        if 'form' not in context:
            context['form'] = AnswerForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('login')

        form = AnswerForm(request.POST, user=request.user, question=self.object)

        if form.is_valid():
            new_answer = form.save()

            target_page = self.object.get_answer_page(new_answer, self.per_page)

            answer_path = f"{self.object.get_absolute_url()}?page={target_page}#answer-{new_answer.id}"
            return redirect(answer_path)

        return self.render_to_response(self.get_context_data(form=form))



class AskQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = AskForm
    template_name = 'questions/ask.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

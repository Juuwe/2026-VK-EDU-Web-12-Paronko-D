from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import View, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import  SearchQuery
import re
from django.conf import settings
from django.template.loader import render_to_string

from .utils import get_centrifugo_token

from .models import Question, QuestionLike, AnswerLike, Answer
from .forms import AskForm, AnswerForm
from django.http import JsonResponse

from .tasks import send_new_answer_notification_task, notify_centrifugo_new_answer



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
        return Question.objects.with_user_vote(self.request.user).select_related('author').prefetch_related('tags').all()

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
        return Question.objects.hot().with_user_vote(self.request.user).select_related('author').prefetch_related('tags')

class ByTagView(BaseQuestionListView):
    template_name = 'questions/tag.html'

    def get_queryset(self):
        return Question.objects.tag(self.kwargs['tag_name']).with_user_vote(self.request.user).select_related('author').prefetch_related('tags')

    def get_extra_context(self):
        return {'tag_name': self.kwargs['tag_name']}

class DetailQuestionView(DetailView):
    model = Question
    template_name = 'questions/question.html'
    per_page = 5

    def get_queryset(self):
        return super().get_queryset().with_user_vote(self.request.user).select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        answers_queryset = self.object.answers.with_user_vote(user).select_related('author').best()
        page_obj = paginate(answers_queryset, self.request, per_page=self.per_page)
        context['page_obj'] = page_obj

        context.update({
            'page_obj': page_obj,
            'answers': page_obj.object_list,
            'centrifugo_token': get_centrifugo_token(self.request.user.id if self.request.user.is_authenticated else None),
            'centrifugo_ws_url': settings.CENTRIFUGO_WS_URL,
        })

        if 'form' not in context:
            context['form'] = AnswerForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('login')

        self.object = self.get_object()
        form = AnswerForm(request.POST, user=request.user, question=self.object)

        if form.is_valid():
            new_answer = form.save()
            target_page = self.object.get_answer_page(new_answer, self.per_page)

            self._send_notifications(request, new_answer, target_page)

            answer_path = f"{self.object.get_absolute_url()}?page={target_page}#answer-{new_answer.id}"
            return redirect(answer_path)

        return self.render_to_response(self.get_context_data(form=form))

    def _send_notifications(self, request, answer, target_page):
        answer_html = render_to_string(
            'questions/partials/answer_card.html',
            {'answer': answer,
             'is_websocket': True},
            request=request
        )
        notify_centrifugo_new_answer.delay(
            question_id=self.object.id,
            author_name=request.user.profile.nickname,
            html_template=answer_html,
            target_page=target_page
        )

        base_url = f"{request.scheme}://{request.get_host()}"
        answer_path = f"{self.object.get_absolute_url()}?page={target_page}#answer-{answer.id}"
        send_new_answer_notification_task.delay(
            answer_id=answer.id,
            base_url=base_url,
            answer_path=answer_path
        )

class AskQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = AskForm
    template_name = 'questions/ask.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class BaseLikeView(View):
    model = None
    like_model = None

    def post(self, request, object_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'err', 'error': 'Auth required'}, status=401)

        obj = get_object_or_404(self.model, pk=object_id)

        like_value = int(request.POST.get('value'))

        if abs(like_value) != 1:
            return JsonResponse({'status': 'err', 'error': 'Invalid value'}, status=400)

        action = self.like_model.objects.add_vote(user=request.user.profile, object=obj, new_value=like_value)

        return JsonResponse({
            'new_rating': obj.rating,
            'action': action,
            'status': 'ok'
        })

class QuestionLikeView(BaseLikeView):
    model = Question
    like_model = QuestionLike

class AnswerLikeView(BaseLikeView):
    model = Answer
    like_model = AnswerLike


class MarkCorrectView(LoginRequiredMixin, View):
    def post(self, request, answer_id):
        is_correct, error = Answer.objects.toggle_correct(
            user=request.user,
            answer_id=answer_id
        )

        if error:
            status_code = 404 if "not exist" in error else 403
            return JsonResponse({'status': 'err', 'error': error}, status=status_code)

        return JsonResponse({'status': 'ok', 'is_correct': is_correct})

def question_search_autocomplete(request):
    query_text = request.GET.get('q', '').strip()

    if len(query_text) < 2:
        return JsonResponse({'results': []})

    clean_words = re.sub(r'[^\w\s]', '', query_text).split()
    if not clean_words:
        return JsonResponse({'results': []})

    clean_words[-1] += ':*'
    raw_query = ' & '.join(clean_words)

    query = SearchQuery(raw_query, config='simple', search_type='raw')

    questions = Question.objects.filter(
        search_vector=query
    ).only('id', 'title')[:10]

    if not questions:
        return JsonResponse({'results': []})

    results = [
        {
            'id': q.id,
            'title': q.title,
            'url': q.get_absolute_url()
        }
        for q in questions
    ]

    return JsonResponse({'results': results})

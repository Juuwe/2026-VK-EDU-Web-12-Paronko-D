from django.urls import path
from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotView.as_view(), name='hot'),
    path('tag/<str:tag_name>/', views.ByTagView.as_view(), name='tag'),
    path('question/<int:pk>/', views.DetailQuestionView.as_view(), name='question'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
    path('question/<int:object_id>/like/', views.QuestionLikeView.as_view(), name='question_like'),
    path('answer/<int:object_id>/like/', views.AnswerLikeView.as_view(), name='answer_like'),
    path('answer/<int:answer_id>/correct/', views.MarkCorrectView.as_view(), name='mark_correct')
]

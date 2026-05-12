from django.urls import path
from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('hot/', views.HotView.as_view(), name='hot'),
    path('tag/<str:tag_name>/', views.ByTagView.as_view(), name='tag'),
    path('question/<int:pk>/', views.DetailQuestionView.as_view(), name='question'),
    path('ask/', views.AskQuestionView.as_view(), name='ask'),
]

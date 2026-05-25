from django.contrib import admin
from .models import Question, Answer, Tag, QuestionLike, AnswerLike

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'created_at', 'answers_count', 'rating')
    search_fields = ('title', 'content', 'author__user__username')
    list_filter = ('created_at', 'tags')

    raw_id_fields = ('author',)
    list_select_related = ('author', 'author__user')
    list_prefetch_related = ('tags')

    class AnswerInline(admin.TabularInline):
        model = Answer
        extra = 0
        raw_id_fields = ('author',)

    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('author', 'question', 'get_snippet', 'is_correct', 'rating', 'created_at')
    search_fields = ('content', 'author__user__username', 'question__title')
    list_filter = ('created_at', 'is_correct')

    raw_id_fields = ('author', 'question')
    list_select_related = ('author', 'question',)

    def get_snippet(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + "..."

        return obj.content

    get_snippet.short_description = "Текст ответа"

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'value', 'created_at')
    search_fields = ('user', 'question')
    list_filter = ('created_at', 'value')

    raw_id_fields = ('user', 'question')
    list_select_related = ('user', 'question',)

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer', 'value', 'created_at')
    search_fields = ('user', 'answer')
    list_filter = ('created_at', 'value')

    raw_id_fields = ('user', 'answer')
    list_select_related = ('user', 'answer')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'questions_count',)
    search_fields = ('name',)

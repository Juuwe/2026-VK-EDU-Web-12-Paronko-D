from django.db import models

class QuestionManager(models.Manager):
    def hot(self):
        return self.order_by('-rating')

    def tag(self, tag_name):
        return self.filter(tags__name=tag_name)

class AnswerManager(models.Manager):
    def best(self):
        return self.order_by('-is_correct', '-rating', 'created_at')

class TagManager(models.Manager):
    def popular(self, limit=20):
        return self.order_by('-questions_count')[:limit]

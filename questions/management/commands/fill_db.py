# пользователей — равное ratio;
# вопросов — ratio * 10;
# ответы — ratio * 100;
# тэгов - ratio;
# оценок пользователей - ratio * 200;

from django.db import models
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils import timezone
from django.db.models import Sum, Count, Subquery, OuterRef
from django.db.models.functions import Coalesce

from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from core.models import Profile

fake = Faker()

class Command(BaseCommand):
    def fill_votes(self, update_model, like_model, target_name, user_idcs, target_idcs, count):
        votes = []
        votes_len = 0
        used_pairs = set()

        field_id = f"{target_name}_id"

        while (votes_len < count):
            user_id = random.choice(user_idcs)
            target_id = random.choice(target_idcs)

            if (user_id, target_id) not in used_pairs:
                value = random.choice([-1, 1])
                used_pairs.add((user_id, target_id))

                votes.append(like_model(user_id=user_id, value=value, **{field_id: target_id}))
                votes_len += 1

            if (len(votes) > 50_000):
                like_model.objects.bulk_create(votes)
                votes = []

        if votes:
            like_model.objects.bulk_create(votes)
            votes = []

        votes_sum = like_model.objects.filter(**{field_id: OuterRef('pk')}).values(field_id).annotate(total=Sum('value')).values('total')

        update_model.objects.update(
            rating=Coalesce(Subquery(votes_sum), 0)
        )

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options["ratio"]

        tags = [Tag(name=f"{fake.word()[:10]}_{i}") for i in range(ratio)]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        tags_idcs = list(Tag.objects.values_list('id', flat=True))

        print('Tags are successfully filled')

        users = []
        for i in range(ratio):
            username = f'{fake.user_name()}_{i}'
            users.append(User(username=username, email=fake.email(), password='password123'))
        User.objects.bulk_create(users)
        users = []

        print('Users are successfully filled')

        user_data = User.objects.exclude(username='admin').values_list('id', 'username')

        profiles = [Profile(user_id=id, nickname=username) for id, username in user_data]
        Profile.objects.bulk_create(profiles)
        profiles = []

        print('Profiles are successfully filled')

        profile_idcs = list(Profile.objects.values_list('id', flat=True))
        questions = []
        for i in range(ratio * 10):
            question = Question(author_id=random.choice(profile_idcs),
                                title=fake.sentence(nb_words=5)[:100],
                                content=fake.text(max_nb_chars=1000),
                                rating=0,
                                answers_count=0,
                                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone())
                                )

            questions.append(question)

        Question.objects.bulk_create(questions)
        questions = []

        question_idcs = list(Question.objects.values_list('id', flat=True))

        print('Questions are successfully filled')

        QuestionTagRelation: models.Model = Question.tags.through

        tag_questions = []
        for q_id in question_idcs:
            tags_idcs_sample = random.sample(tags_idcs, k=random.randint(1, 5))

            for t_id in tags_idcs_sample:
                tag_questions.append(QuestionTagRelation(question_id=q_id, tag_id=t_id))

            if len(tag_questions) > 50_000:
                QuestionTagRelation.objects.bulk_create(tag_questions)
                tag_questions = []

        if tag_questions:
            QuestionTagRelation.objects.bulk_create(tag_questions)
            tag_questions = []

        print('QuestionTagRelations are successfully filled')

        answers = []

        questions_data = list(Question.objects.values_list('id', 'author_id', 'created_at'))
        q_info = {q_id: (auth_id, date) for q_id, auth_id, date in questions_data}

        pre_generated_texts = [fake.text(max_nb_chars=2500) for _ in range(200)]
        print('Text for answers are successfully generated')

        for i in range(ratio * 100):
            question_id = random.choice(question_idcs)
            q_author_id, q_created_at = q_info[question_id]

            author_id = random.choice(profile_idcs)
            while (q_author_id == author_id):
                author_id = random.choice(profile_idcs)

            created_at = fake.date_time_between(
                start_date=q_created_at,
                end_date='now',
                tzinfo=timezone.get_current_timezone()
            )

            answer = Answer(author_id=author_id,
                            question_id=question_id,
                            content=random.choice(pre_generated_texts),
                            rating=0,
                            created_at=created_at,
                            is_correct=False
                        )

            answers.append(answer)

            if len(answers) > 50_000:
                Answer.objects.bulk_create(answers)
                answers = []

        if answers:
            Answer.objects.bulk_create(answers)
            answers = []


        print('Answers are successfully filled')

        answers_idcs = list(Answer.objects.values_list('id', flat=True))

        self.fill_votes(Question, QuestionLike, 'question', profile_idcs, question_idcs, ratio * 100)
        print('QuestionLikes are successfully filled')

        self.fill_votes(Answer, AnswerLike, 'answer', profile_idcs, answers_idcs, ratio * 100)
        print('AnswerLikes are successfully filled')

        answers_counts = Answer.objects.filter(question_id=OuterRef('pk')).values('question_id').annotate(cnt=Count('id')).values('cnt')
        Question.objects.update(answers_count=Coalesce(Subquery(answers_counts), 0))

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from .models import Question


@pytest.mark.django_db
def test_old_question_was_published_recently():
    date = timezone.now() - datetime.timedelta(days=1, seconds=1)
    question = Question(pub_date=date)

    assert question.was_published_recently() is False


@pytest.mark.django_db
def test_was_published_recently_with_recent_question():
    date = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    question = Question(pub_date=date)

    assert question.was_published_recently() is True


@pytest.mark.django_db
def test_future_question_was_published_recently():
    date = timezone.now() + datetime.timedelta(days=30)
    question = Question(pub_date=date)

    assert question.was_published_recently() is False


def create_questions_fixture(text, days):
    date = timezone.now() + datetime.timedelta(days=days)
    question_obj = Question.objects.create(question_text=text, pub_date=date)

    return question_obj


@pytest.mark.django_db
def test_no_questions(client):
    response = client.get(reverse('polls:index'))

    assert response.status_code == 200

    assert list(response.context['latest_question_list']) == []


@pytest.mark.django_db
def test_future_question(client):
    question = create_questions_fixture(text='some question', days=5)
    url = reverse('polls:detail', args=(question.id,))
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_question_past(client):
    question_text = "some question"
    create_questions_fixture(text=question_text, days=-30)
    response = client.get(reverse('polls:index'))

    assert bool(response.context['latest_question_list']) is True

    assert response.context['latest_question_list'][0].question_text == question_text

    assert response.status_code == 200


@pytest.mark.django_db
def test_question_future(client):
    create_questions_fixture(text="Some question", days=30)
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context['latest_question_list']) == []


@pytest.mark.django_db
def test_question_past(client):
    past_question = create_questions_fixture(text='some Question.', days=-5)
    url = reverse('polls:detail', args=(past_question.id,))
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_two_questions_past(client):
    question_text_one = "some question 1."
    question_text_two = "some question 2."
    create_questions_fixture(text=question_text_one, days=-30)
    create_questions_fixture(text=question_text_two, days=-5)
    response = client.get(reverse('polls:index'))
    assert response.context['latest_question_list'][0].question_text == question_text_two

    assert response.context['latest_question_list'][1].question_text == question_text_one

    assert response.status_code == 200


@pytest.mark.django_db
def test_question_future_and_past_question(client):
    question = "some question."
    create_questions_fixture(text=question, days=-30)
    create_questions_fixture(text="some other question", days=30)
    response = client.get(reverse('polls:index'))

    assert bool(response.context['latest_question_list']) is True

    assert response.context['latest_question_list'][0].question_text == question

    assert response.status_code == 200

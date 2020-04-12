import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from .models import Question


@pytest.mark.django_db
def test_was_published_recently_with_future_question():
    """
    was_published_recently() returns False for questions whose pub_date
    is in the future.
    """
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    assert future_question.was_published_recently() is False


@pytest.mark.django_db
def test_was_published_recently_with_old_question():
    """
    was_published_recently() returns False for questions whose pub_date
    is older than 1 day.
    """
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    assert old_question.was_published_recently() is False


@pytest.mark.django_db
def test_was_published_recently_with_recent_question():
    """
    was_published_recently() returns True for questions whose pub_date
    is within the last day.
    """
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    assert recent_question.was_published_recently() is True


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


@pytest.mark.django_db
def test_no_questions(client):
    """
    If no questions exist, an appropriate message is displayed.
    """
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context['latest_question_list']) == []


@pytest.mark.django_db
def test_past_question(client):
    """
    Questions with a pub_date in the past are displayed on the
    index page.
    """
    question_text = "Past question."
    create_question(question_text=question_text, days=-30)
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert bool(response.context['latest_question_list']) is True
    assert response.context['latest_question_list'][0].question_text == question_text


@pytest.mark.django_db
def test_future_question(client):
    """
    Questions with a pub_date in the future aren't displayed on
    the index page.
    """
    create_question(question_text="Future question.", days=30)
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context['latest_question_list']) == []


@pytest.mark.django_db
def test_future_question_and_past_question(client):
    """
    Even if both past and future questions exist, only past questions
    are displayed.
    """
    past_question_text = "Past question."
    create_question(question_text=past_question_text, days=-30)
    create_question(question_text="Future question.", days=30)
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert bool(response.context['latest_question_list']) is True
    assert response.context['latest_question_list'][0].question_text == past_question_text


@pytest.mark.django_db
def test_two_past_questions(client):
    """
    The questions index page may display multiple questions.
    """
    question_text_one = "Past question 1."
    question_text_two = "Past question 2."
    create_question(question_text=question_text_one, days=-30)
    create_question(question_text=question_text_two, days=-5)
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert response.context['latest_question_list'][0].question_text == question_text_two
    assert response.context['latest_question_list'][1].question_text == question_text_one


@pytest.mark.django_db
def test_future_question(client):
    """
    The detail view of a question with a pub_date in the future
    returns a 404 not found.
    """
    future_question = create_question(question_text='Future question.', days=5)
    url = reverse('polls:detail', args=(future_question.id,))
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_past_question(client):
    """
    The detail view of a question with a pub_date in the past
    displays the question's text.
    """
    past_question = create_question(question_text='Past Question.', days=-5)
    url = reverse('polls:detail', args=(past_question.id,))
    response = client.get(url)
    assert response.status_code == 200

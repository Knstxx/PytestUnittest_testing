import pytest
from django.test.client import Client
from django.urls import reverse
from news.models import News, Comment
from django.contrib.auth import get_user_model
from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING


User = get_user_model()


@pytest.mark.django_db
def test_user_cant_create_comment(form_data1, client, news):
    client.post(reverse('news:detail', args=[news.id]), data=form_data1)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(not_author_client, form_data1, news):
    not_author_client.post(reverse('news:detail', args=[news.id]), data=form_data1)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(reverse('news:detail', args=[news.id]), data=bad_words_data)
    form_errors = response.context.get('form').errors.get('text')
    assert form_errors[0] == WARNING
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.parametrize(
    'par_client, expected_count',
    (
        (pytest.lazy_fixture('author_client'), 0),
        (pytest.lazy_fixture('not_author_client'), 1)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete',),
)
@pytest.mark.django_db
def test_users_can_delete_comment(name, par_client, expected_count, comment):
    delete_url = reverse(name, args=[comment.id])
    par_client.delete(delete_url)
    assert Comment.objects.count() == expected_count


@pytest.mark.parametrize(
    'par_client, expected_answ',
    (
        (pytest.lazy_fixture('author_client'), 'Новый текст комментария'),
        (pytest.lazy_fixture('not_author_client'), 'Текст комментария')
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit',),
)
@pytest.mark.django_db
def test_author_can_edit_comment(name, new_form_data, par_client, expected_answ, comment):
    edit_url = reverse(name, args=[comment.id])
    par_client.post(edit_url, data=new_form_data)
    comment.refresh_from_db()
    assert comment.text == expected_answ

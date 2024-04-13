import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


User = get_user_model()


@pytest.mark.django_db
def test_user_cant_create_comment(form_data, client, news):
    comments_count = Comment.objects.count()

    client.post(reverse('news:detail', args=[news.id]), data=form_data)

    assert comments_count == Comment.objects.count()


@pytest.mark.django_db
def test_user_can_create_comment(not_author_client, form_data, news):
    comments_count = Comment.objects.count()

    not_author_client.post(reverse('news:detail', args=[news.id]),
                           data=form_data)

    assert comments_count + 1 == Comment.objects.count()


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count = Comment.objects.count()

    response = author_client.post(reverse('news:detail', args=[news.id]),
                                  data=bad_words_data)

    form_errors = response.context.get('form').errors.get('text')
    assert form_errors[0] == WARNING
    assert comments_count == Comment.objects.count()


@pytest.mark.parametrize(
    'par_client, delta_count',
    (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('not_author_client'), 0)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete',),
)
@pytest.mark.django_db
def test_users_can_delete_comment(name, par_client, delta_count, comment):
    comments_count = Comment.objects.count()
    delete_url = reverse(name, args=[comment.id])

    par_client.delete(delete_url)

    assert Comment.objects.count() == comments_count - delta_count


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
def test_author_can_edit_comment(name,
                                 new_form_data,
                                 par_client,
                                 expected_answ,
                                 comment
                                 ):
    edit_url = reverse(name, args=[comment.id])

    par_client.post(edit_url, data=new_form_data)

    comment.refresh_from_db()
    assert comment.text == expected_answ

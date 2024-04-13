import pytest
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_main_page_news_count(client):
    for i in range(11):
        News.objects.create(
            title=f'News {i}',
            text=f'Text {i}',
        )

    response = client.get(reverse('news:home'))

    assert len(response.context['object_list']) <= NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    for i in range(5):
        News.objects.create(
            title=f'News {i}',
            text=f'Text {i}',
            date=timezone.now() - timezone.timedelta(days=i)
        )

    response = client.get(reverse('news:home'))

    news_dates = [news.date for news in response.context['object_list']]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news, comment):
    for i in range(5):
        Comment.objects.create(
            news=comment.news,
            author=comment.author,
            text=f'Comment {i}',
            created=timezone.now() - timezone.timedelta(days=i)
        )
    detail_url = reverse('news:detail', args=(news.id,))

    response = client.get(detail_url)

    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db
def test_comment_form_availability(news, author_client):
    response = author_client.get(reverse('news:detail', args=[news.id]))

    assert 'form' in response.context


@pytest.mark.django_db
def test_comment_form_unavailability(news, client):
    response = client.get(reverse('news:detail', args=[news.id]))

    assert 'form' not in response.context

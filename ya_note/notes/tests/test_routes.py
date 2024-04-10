from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='Slug',
                                       author=cls.author
                                       )

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_specific_pages_available_for_author(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_available_for_authenticated_user(self):
        self.client.force_login(self.reader)
        pages = ['notes:list', 'notes:add', 'notes:success']
        for page in pages:
            with self.subTest(name=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_user(self):
        login_url = reverse('users:login')
        pages = [('notes:list', None),
                 ('notes:add', None),
                 ('notes:success', None),
                 ('notes:detail', (self.note.id,)),
                 ('notes:edit', (self.note.id,)),
                 ('notes:delete', (self.note.id,)),
                 ]
        for page, arg in pages:
            with self.subTest(name=page):
                url = reverse(page, args=arg)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_login_pages_available(self):
        pages = ['users:signup',
                 'users:login',
                 'users:logout'
                 ]
        for page in pages:
            with self.subTest(name=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, HTTPStatus.OK)

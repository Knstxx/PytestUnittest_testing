from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note_reader = Note.objects.create(title='Заголовок1',
                                              text='Текст1',
                                              slug='Slug1',
                                              author=cls.reader
                                              )
        cls.note_author = Note.objects.create(title='Заголовок2',
                                              text='Текст2',
                                              slug='Slug2',
                                              author=cls.author
                                              )

    def test_note_passed_to_note_list_page(self):
        note_list_url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(note_list_url)
        self.assertIn(self.note_author, response.context['object_list'])

    def test_only_author_notes_in_user_notes_list(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertIn(self.note_author, response.context['object_list'])
        self.assertNotIn(self.note_reader, response.context['object_list'])

    def test_forms_passed_to_create_and_edit_pages(self):
        add_url = reverse('notes:add')
        edit_url = reverse('notes:edit', args=[self.note_author.slug])
        self.client.force_login(self.author)
        create_response = self.client.get(add_url)
        edit_response = self.client.get(edit_url)
        self.assertIn('form', create_response.context)
        self.assertIn('form', edit_response.context)

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='Slug',
                                       author=cls.author
                                       )
        cls.url_detail = reverse('notes:add')
        cls.user = User.objects.create(username='Гена На')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.data_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'Slug2',
            'author': cls.user
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url_detail, data=self.data_note)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url_detail, data=self.data_note)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_cannot_create_note_with_duplicate_slug(self):
        self.data_note['slug'] = self.note.slug
        self.auth_client.post(self.url_detail, data=self.data_note)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_automatic_slug_creation(self):
        del self.data_note['slug']
        self.auth_client.post(self.url_detail, data=self.data_note)
        latest_note = Note.objects.latest('id')
        self.assertEqual(latest_note.slug, slugify(self.data_note['title']))

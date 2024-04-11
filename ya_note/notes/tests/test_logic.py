from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class NoteTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.url_detail = reverse('notes:add')
        cls.user = User.objects.create(username='Гена На')
        cls.other_user = User.objects.create(username='Другой Гена На')
        cls.auth_client = Client()
        cls.other_auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.other_auth_client.force_login(cls.other_user)
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='Slug',
                                       author=cls.user
                                       )
        cls.data_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'Slug2',
            'author': cls.user
        }
        cls.up_data_note = {
            'title': 'Заголовок новый',
            'text': 'Текст новый',
        }

    def test_anonymous_user_cant_create_note(self):
        note_count = Note.objects.count()

        self.client.post(self.url_detail, data=self.data_note)

        self.assertEqual(note_count, Note.objects.count())

    def test_user_can_create_note(self):
        note_count = Note.objects.count()

        self.auth_client.post(self.url_detail, data=self.data_note)

        self.assertEqual(note_count + 1, Note.objects.count())

    def test_cannot_create_note_with_duplicate_slug(self):
        self.data_note['slug'] = self.note.slug
        note_count = Note.objects.count()

        self.auth_client.post(self.url_detail, data=self.data_note)

        self.assertEqual(note_count, Note.objects.count())

    def test_automatic_slug_creation(self):
        del self.data_note['slug']

        self.auth_client.post(self.url_detail, data=self.data_note)

        latest_note = Note.objects.latest('id')
        self.assertEqual(latest_note.slug, slugify(self.data_note['title']))

    def test_user_can_edit_own_note(self):
        edit_url = reverse('notes:edit', args=[self.note.slug])

        self.auth_client.post(edit_url, data=self.up_data_note)
        self.note.refresh_from_db()

        self.assertEqual(self.note.title, self.up_data_note['title'])
        self.assertEqual(self.note.text, self.up_data_note['text'])

    def test_user_cannot_edit_other_users_note(self):
        edit_url = reverse('notes:edit', args=[self.note.slug])

        self.other_auth_client.post(edit_url, data=self.up_data_note)
        self.note.refresh_from_db()

        self.assertNotEqual(self.note.title, self.up_data_note['title'])
        self.assertNotEqual(self.note.text, self.up_data_note['text'])

    def test_user_can_delete_own_note(self):
        delete_url = reverse('notes:delete', args=[self.note.slug])
        note_count = Note.objects.count()

        self.auth_client.post(delete_url)

        self.assertEqual(note_count - 1, Note.objects.count())

    def test_user_cannot_delete_other_users_note(self):
        delete_url = reverse('notes:delete', args=[self.note.slug])
        note_count = Note.objects.count()

        self.other_auth_client.post(delete_url)

        self.assertEqual(note_count, Note.objects.count())

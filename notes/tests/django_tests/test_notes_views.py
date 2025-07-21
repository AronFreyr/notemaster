from django.test.testcases import TestCase
from notes.models import Document, Tag, Tagmap
from django.urls import reverse
from django.contrib.auth.models import User


class CreateDocViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_pass')
        self.create_doc_url = reverse('notes:create_doc')
        self.client.login(username='test_user', password='test_pass')

    def test_create_doc_get(self):
        response = self.client.get(self.create_doc_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/create-document.html')

    def test_create_doc_post_success(self):
        data = {
            'document_name': 'Test Doc',
            'document_text': 'Some text',
            'new_tag': 'TestTag'
        }
        response = self.client.post(self.create_doc_url, data)
        self.assertEqual(Document.objects.count(), 1)
        self.assertRedirects(response, reverse('notes:display_doc',
                                               kwargs={'doc_id': Document.objects.first().id}))

    def test_create_doc_post_duplicate_name(self):
        Document.objects.create(document_name='Test Doc', document_text='Text',
                                document_created_by=self.user, document_last_modified_by=self.user)

        data = {
            'document_name': 'Test Doc',
            'document_text': 'Other text',
            'new_tag': 'TestTag'
        }

        response = self.client.post(self.create_doc_url, data)
        self.assertContains(response, 'This name is already taken')

    def test_create_doc_with_blank_name(self):
        data = {
            'document_name': '',
            'document_text': 'Some text',
            'new_tag': 'TestTag'
        }
        response = self.client.post(self.create_doc_url, data)
        self.assertContains(response, 'This field is required.')

from django.core.paginator import Page
from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch

from . import util
from .forms import EditEntryForm, NewEntryForm

# Views Tests
class IndexViewTest(TestCase):
    def test_index_view_with_entries(self):
        entries = ["Entry1", "Entry2", "Entry3", "Entry4", "Entry5", "Entry6", "Entry7", "Entry8", "Entry9", "Entry10", "Entry11"]

        # Mock the 'list_entries' function to return the list of entries
        with patch.object(util, 'list_entries', return_value=entries):
            response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/index.html')

        # Check if the entries are paginated correctly (assuming 10 entries per page)
        self.assertIsInstance(response.context['entries'], Page)
        self.assertEqual(len(response.context['entries']), 10)  # Check the number of entries on the page
        self.assertEqual(response.context['entries'].paginator.num_pages, 2)  # Check the number of pages

    def test_index_view_without_entries(self):
        # Mock the 'list_entries' function to return an empty list
        with patch.object(util, 'list_entries', return_value=[]):
            response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/index.html')

        # Check if there are no entries displayed on the page
        self.assertEqual(len(response.context['entries']), 0)  # Check the number of entries on the page
        self.assertEqual(response.context['entries'].paginator.num_pages, 1)  # Check the number of pages

class EntryViewTest(TestCase):
    def test_entry_view_with_existing_entry(self):
        title = "Test Entry"
        content = "This is a test entry content."

        # Mock the 'get_entry' function to return the test entry content
        with patch.object(util, 'get_entry', return_value=content):
            response = self.client.get(reverse('entry', args=[title]))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/entry.html')

        # Check if the rendered content matches the test entry content
        self.assertContains(response, title)  # Check if the title is displayed
        self.assertContains(response, content)  # Check if the content is displayed

    def test_entry_view_with_nonexistent_entry(self):
        # Define a test entry title that does not exist
        title = "Nonexistent Entry"

        # Mock the 'get_entry' function to return None (indicating a nonexistent entry)
        with patch.object(util, 'get_entry', return_value=None):
            response = self.client.get(reverse('entry', args=[title]))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/error.html')

        # Check if the error message indicates that the entry was not found
        self.assertContains(response, title)  # Check if the title is displayed
        self.assertContains(response, "Not Found")  # Check if the "Not Found" message is displayed

class CreateViewTest(TestCase):
    def setUp(self):
        self.test_data = {
            'title': 'Test Entry',
            'content': 'Test content',
        }

    def test_create_view_GET(self):
        response = self.client.get(reverse('create'))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/create.html')

        # Check if the form is an instance of NewEntryForm
        self.assertIsInstance(response.context['form'], NewEntryForm)

    def test_create_view_POST_valid_data(self):
        # Mock the 'get_entry' and 'save_entry' functions
        with patch.object(util, 'get_entry', return_value=None):
            with patch.object(util, 'save_entry', return_value=None) as mock_save_entry:
                response = self.client.post(reverse('create'), data=self.test_data)

                self.assertEqual(response.status_code, 302)  # Check if the view redirects to the entry page

                # Check if the 'save_entry' function was called with the updated content
                mock_save_entry.assert_called_once_with(self.test_data['title'], self.test_data['content'])

    def test_create_view_POST_existing_entry(self):
        # Mock the 'get_entry' and 'save_entry' functions
        with patch.object(util, 'get_entry', return_value="Existing Content"):
            response = self.client.post(reverse('create'), data=self.test_data)                

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used (re-rendering the create form)
        self.assertTemplateUsed(response, 'encyclopedia/create.html')

        # Check if the error message is displayed
        self.assertContains(response, 'Already Exists')

    def test_create_view_POST_invalid_data(self):
        invalid_form_data = {
            'content': 'Invalid content.',
        }

        # Mock the 'get_entry' function to return None (indicating a new entry)
        with patch.object(util, 'get_entry', return_value=None):
            response = self.client.post(reverse('create'), data=invalid_form_data)

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used (re-rendering the create form)
        self.assertTemplateUsed(response, 'encyclopedia/create.html')

        # Check if the form has errors
        self.assertTrue(response.context['form'].errors)

class EditViewTest(TestCase):
    def setUp(self):
        self.test_data = {
            'title': 'Test Entry',
            'original_content': 'Test content',
            'updated_content': 'Updated content.'
        }

    def test_edit_view_GET(self):
        # Mock the 'get_entry' function to return test content
        with patch.object(util, 'get_entry', return_value=self.test_data['original_content']):
            response = self.client.get(reverse('edit', args=[self.test_data['title']]))

        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'encyclopedia/edit.html')

        # Check if the form is initialized with the entry's title and content
        self.assertIsInstance(response.context['form'], EditEntryForm)
        self.assertEqual(response.context['form'].initial['title'], self.test_data['title'])
        self.assertEqual(response.context['form'].initial['content'], self.test_data['original_content'])

    def test_edit_view_POST_valid_data(self):
        # Mock the 'get_entry' and 'save_entry' functions
        with patch.object(util, 'get_entry', return_value=self.test_data['original_content']):
            with patch.object(util, 'save_entry', return_value=None) as mock_save_entry:
                data = {
                    'title': self.test_data['title'],
                    'content': self.test_data['updated_content']
                }
                response = self.client.post(reverse('edit', args=[self.test_data['title']]), data=data)

                self.assertEqual(response.status_code, 302)  # Check if the view redirects to the entry page

                # Check if the 'save_entry' function was called with the updated content
                mock_save_entry.assert_called_once_with(self.test_data['title'], self.test_data['updated_content'])

    def test_edit_view_POST_invalid_data(self):
        response = self.client.post(reverse('edit', args=[self.test_data['title']]), data={'title': self.test_data['title'], 'content': ""})
        self.assertEqual(response.status_code, 200)  # Check if the view returns a 200 status code

        # Check if the correct template is used (re-rendering the edit form)
        self.assertTemplateUsed(response, 'encyclopedia/edit.html')

        # Check if the form has errors
        self.assertTrue(response.context['form'].errors)

# Forms Tests
class CreateEntryFormTest(TestCase):
    def test_create_form_valid_data(self):
        form_data = {
            'title': 'Test Title',
            'content': 'This is a test content.',
        }

        form = NewEntryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_form_invalid_data(self):
        form_data = {
            'content': 'This is a test content.',
        }

        form = NewEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

class EditEntryFormTest(TestCase):
    def test_edit_form_valid_data(self):
        form_data = {
            'title': 'Test Title',
            'content': 'This is a test content.',
        }

        form = EditEntryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_edit_form_invalid_data(self):
        form_data = {
            'content': 'This is a test content.',
        }

        form = EditEntryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
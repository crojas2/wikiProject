from django.test import TestCase
from django.core.paginator import Page
from django.urls import reverse
from unittest.mock import patch

from . import util

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

from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_displays_challenges_and_project_folders(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desafíos Disponibles")
        self.assertContains(response, "Carpetas del proyecto")
        self.assertContains(response, "templates")
        self.assertContains(response, "static")

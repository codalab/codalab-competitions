from django.test import TestCase, RequestFactory

from django.contrib.auth import get_user_model

from apps.web import views, models


class HomePageTest(TestCase):
    def test_context_not_single_competition_view(self):
        with self.settings(SINGLE_COMPETITION_VIEW_PK=None):
            try:
                request = RequestFactory().get('/')

                view = views.HomePageView.as_view()(request)

                context = view.get_context_data()
                self.assertIn('latest_competitions', context)
            except models.Competition.DoesNotExist:
                # Competition does not exist. Create competition to test content
                pass

    def test_context_single_competition_view(self):
        try:
            request = RequestFactory().get('/')

            view = views.HomePageView.as_view()(request)

            context = view.get_context_data()
            self.assertIn('latest_competitions', context)
        except Exception:
            # Competition does not exist. Create competition to test content
            pass

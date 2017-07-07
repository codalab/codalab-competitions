from django.test import TestCase
from apps.web.utils import docker_image_clean


class DockerImageSanitationTests(TestCase):

    def _sanitize(self, str, result):
        self.assertEquals(docker_image_clean(str), result)

    def test_docker_image_sanitation(self):
        # Baseline
        self._sanitize("continuumio/anaconda:4.3.0", "continuumio/anaconda:4.3.0")
        # Test cases
        self._sanitize("      continuumio/anaconda:4.3.0           ", "continuumio/anaconda:4.3.0")
        self._sanitize("###continuumio###/###anaconda:4.3.0###", "continuumio/anaconda:4.3.0")
        self._sanitize("continuumio/anaconda:4.3.0 && sudo rm -rf /", "continuumio/anaconda:4.3.0")
        self._sanitize("continuumio/anaconda:4.3.0 && ls -all || ls.txt", "continuumio/anaconda:4.3.0")
        self._sanitize("continuumio/ anaconda:4.3.0", "continuumio/")
        self._sanitize("'sudo bash'", "sudo")
        self._sanitize("", "")
        self._sanitize(" ", "")
        self._sanitize("continuumio/anaconda:4.3.0", "continuumio/anaconda:4.3.0")
        self._sanitize(" " * 100, "")
        self._sanitize(" " * 1000, "")
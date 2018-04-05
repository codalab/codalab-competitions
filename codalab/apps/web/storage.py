import os

from storages.backends.gcloud import GoogleCloudStorage


class CodalabGoogleCloudStorage(GoogleCloudStorage):
    def url(self, path, *args, **kwargs):
        if path == '':
            return os.path.join('https://storage.googleapis.com', self.bucket.name)
        return super(CodalabGoogleCloudStorage, self).url(path, *args, **kwargs)

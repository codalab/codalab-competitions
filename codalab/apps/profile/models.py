from django.db import models
from django.contrib.auth import models as auth_models
from apps.authenz.models import ClUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from sorl.thumbnail import ImageField

class UserProfile(models.Model):
    # Links UserProfile to a Codalab User model instance.
    user = models.OneToOneField(ClUser, primary_key=True)

    # fs = FileSystemStorage(location='/Users/xbaro/Documents/GitRepository/codalab/codalab/media/photos')
    # fs = FileSystemStorage(location='media')

    # Additional attributes for user profile.
    affiliation = models.CharField(max_length=200,blank=True)
    location = models.CharField(max_length=200,blank=True) # Use CountryField or more complex model (https://djangosnippets.org/snippets/912/)
    #picture = models.ImageField(upload_to='profile_images', blank=True, default='') # Can be stored in Azure. Put a default image for profiles?
    picture = models.ImageField(upload_to='profile_images', blank=True, default='')
    biography= models.TextField(blank=True)
    website = models.URLField(blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username


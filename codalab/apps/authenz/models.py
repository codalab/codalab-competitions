
from django.contrib.auth import models as auth_models


class ClUser(auth_models.AbstractUser):

    # Additional attributes for user profile.
    affiliation = models.CharField(max_length=200,blank=True)
    location = models.CharField(max_length=200,blank=True) # Use CountryField or more complex model (https://djangosnippets.org/snippets/912/)
    picture = models.ImageField(upload_to='profile_images', blank=True, default='') # Can be stored in Azure. Put a default image for profiles?
    biography= models.TextField(blank=True)
    website = models.URLField(blank=True)

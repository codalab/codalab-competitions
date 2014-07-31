from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from apps.profile.models import UserProfile,ClUser
from apps.profile import forms

@login_required
def profile(request):
    context = RequestContext(request)

    if request.method == 'POST':

        user_form = forms.UserForm(instance=request.user, data=request.POST)
        if hasattr(request.user, 'userprofile'):
            profile_form = forms.UserProfileForm(instance=request.user.userprofile, data=request.POST, files=request.FILES)
        else:
            profile_form = forms.UserProfileForm(data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            user_profile = profile_form.save(commit=False)
            user_profile.user = user
            user_profile.picture = profile_form.cleaned_data['picture']

            # Now we save the UserProfile model instance.
            user_profile.save()

            # Update the profile form to see the picture
            profile_form = forms.UserProfileForm(instance=request.user.userprofile, data=request.POST, files=request.FILES)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print user_form.errors, profile_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        user_form = forms.UserForm(instance=request.user)
        if hasattr(request.user, 'userprofile'):
            profile_form = forms.UserProfileForm(instance=request.user.userprofile)
        else:
            profile_form = forms.UserProfileForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('profile.html', {'user_form': user_form, 'profile_form': profile_form, 'user': request.user}, context)
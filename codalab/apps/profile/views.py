from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from apps.profile.models import UserProfile,ClUser
from apps.profile import forms

@login_required
def profile(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':

        user_form = forms.UserForm(instance=request.user,data=request.POST)
        profile_form = forms.UserProfileForm(instance=request.user.userprofile,data=request.POST)
    
        # Have we been provided with a valid form?
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save(commit=False)

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            #if user.password:
            #    user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()
        else:
            # The supplied form contained errors - just print them to the terminal.
            print user_form.errors, profile_form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        user_form = forms.UserForm(instance=request.user)
        profile_form = forms.UserProfileForm(instance=request.user.userprofile)

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('profile.html', {'user_form': user_form, 'profile_form': profile_form}, context)
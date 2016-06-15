Authentication
==============

Models
------
.. automodule:: apps.authenz.models
	:members:
	:exclude-members: ClUser

	.. autoclass:: ClUser()

Views
-----
.. automodule:: apps.authenz.views
	:members:
	:undoc-members:
	:private-members:
	:exclude-members: new_user_signup, on_user_logged_in, InfoApi, ValidationApi

	.. autoclass:: InfoApi()
		:members:
		:private-members:
   		:special-members:
	.. autoclass:: ValidationApi()
		:members:
		:private-members:
   		:special-members:
	.. autofunction:: new_user_signup(sender, user)
	.. autofunction:: on_user_logged_in(sender, user)

Forms
-----
.. automodule:: apps.authenz.forms
	:members:
	:exclude-members: CodalabSignupForm

	.. autoclass:: CodalabSignupForm()

OAuth
-----
.. automodule:: apps.authenz.oauth
	:members:
	:exclude-members: Validator

	.. autoclass:: Validator()
		:members:
		:exclude-members: validate_scopes, get_default_scopes

		.. automethod:: validate_scopes(self, client_id, scopes, client, request)
Forum
=====

Models
------
.. automodule:: apps.forums.models
	:members:
	:exclude-members: Forum, Post, Thread

	.. autoclass:: Forum()
		:members:
	.. autoclass:: Post()
		:members:
	.. autoclass:: Thread()
		:members:

Views
-----
.. automodule:: apps.forums.views

	.. autoclass:: ForumBaseMixin()
		:members:
	.. autoclass:: ForumDetailView()
	.. autoclass:: CreatePostView()
	.. autoclass:: CreateThreadView()
	.. autoclass:: ThreadDetailView()

Forms
-----
.. automodule:: apps.forums.forms
	:members:
	:exclude-members: ThreadForm, PostForm

	.. autoclass:: ThreadForm()
		:members:
	.. autoclass:: PostForm()
		:members:

Utils
-------
.. automodule:: apps.forums.helpers
	:members:
	:exclude-members: send_mail

	.. autofunction:: send_mail()
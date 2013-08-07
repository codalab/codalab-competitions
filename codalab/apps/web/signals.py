from django import dispatch

do_submission = dispatch.Signal(providing_args=['instance'])
submission_accepted = dispatch.Signal(providing_args=['submission_id'])
submission_rejected = dispatch.Signal(providing_args=['submission_id'])

from __future__ import absolute_import

from celerysrv import celery

@celery.task(name='competition.validate_submission')
def validate_submission(url):
    """
    Will validate the format of a submission.
    """
    print "VALIDATION %s" % url
    return url

@celery.task(name='competition.evaluation_submission')
def evaluate_submission(url):
    # evaluate(inputdir, standard, outputdir)
    return url

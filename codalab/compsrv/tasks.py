from celery import task

@task
def evaluate_submission(location):
    # evaluate(inputdir,standard,outputdir)
    

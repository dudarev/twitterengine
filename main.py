import logging, os, sys

from google.appengine.ext.webapp import util

for k in [k for k in sys.modules if k.startswith('django')]:
    del sys.modules[k]

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path = [
    PROJECT_ROOT + '/lib/django',
    PROJECT_ROOT + '/lib/django.zip',
    PROJECT_ROOT + '/project',
] + sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
import django.core.signals
import django.db
import django.dispatch.dispatcher

def log_exception(sender, request, *args, **kwargs):
    logging.exception('Exception in request: %s' % request.path)

django.core.signals.got_request_exception.connect(log_exception)
django.core.signals.got_request_exception.disconnect(django.db._rollback_on_exception)

def main():
    application = django.core.handlers.wsgi.WSGIHandler()
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

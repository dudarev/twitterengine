from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('project.views',
    url(r'^$', 'index', name='index'),
    url(r'^rss$', 'rss', name='rss_feed'),
    url(r'^import$', 'do_import'),
)


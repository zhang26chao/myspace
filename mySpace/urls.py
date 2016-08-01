from django.conf.urls import patterns, include, url
from django.contrib import admin
from blog.views import blog
from blog.views import index
from blog.views import tag
from blog.views import about
from blog.views import gallery
from blog.views import code
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mySpace.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    url(r'^$', index),
    url(r'^index/$', index),
    url(r'^blog/(\d*)$', blog),
    url(r'^tag/(\d*)$', tag),
    url(r'^about/$', about),
    url(r'^gallery/(\d*)$', gallery),
    url(r'^code/$', code),
    (r'^search/', include('haystack.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG is False:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }),
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    )

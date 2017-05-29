from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Examples:
    url(r'^$', 'dashboard.views.home', name='home'),
    url(r'^question/(?P<id>\d+)/$', 'questions.views.single', name='question_single'),
    url(r'^question/$', 'questions.views.home', name='question_home'),
    url(r'^result/$', 'dashboard.views.result', name='user_result'),
    url(r'^contact/$', 'newsletter.views.contact', name='contact'),
    url(r'^about/$', 'depressionassesment.views.about', name='about'),
    url(r'^test/$', 'dashboard.views.test', name='test'),
    url(r'^user-agreement/$', 'dashboard.views.user_agreement', name='user_agreement'),

  


    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # url(r'^accounts/', include('registration.backends.simple.urls')),
]

# if settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


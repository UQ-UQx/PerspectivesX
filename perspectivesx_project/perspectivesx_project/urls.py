from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Examples:
    # url(r'^$', 'perspectivesx_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^perspectivesX/',include('perspectivesx.urls')),
    url(r'^api/', include('perspectivesx.apiurls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'perspectivesx_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^perspectivesX/',include('perspectivesx.urls')),
    url(r'^api/', include('perspectivesx.apiurls'))

]

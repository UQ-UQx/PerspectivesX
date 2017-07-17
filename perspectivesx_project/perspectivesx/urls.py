from django.conf.urls import url
from .views import add_activity,index,student_submission,create_template,curate_item

urlpatterns = [
   url(r'^add_activity/$', add_activity, name='add_activity'),
   url(r'^$',index, name = 'index'),
   url(r'^submission/(?P<activity_name_slug>[\w\-]+)/$',student_submission,name = 'submission'),
   url(r'^create_template/$',create_template, name = 'create_template'),
   url(r'^curate/(?P<activity_name_slug>[\w\-]+)/$',curate_item, name = "Item Curator"),
   url(r'^curate/(?P<activity_name_slug>[\w\-]+)/(?P<item>[\w\-]+)/$',curate_item, name = "Defined Item Curator")]
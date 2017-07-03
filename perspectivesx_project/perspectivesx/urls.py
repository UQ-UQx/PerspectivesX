from django.conf.urls import url
from perspectivesx import views

urlpatterns = [
   url(r'^add_activity/$', views.add_activity, name='add_activity'),
   url(r'^$',views.index, name = 'index'),
   url(r'^submission/(?P<activity_name_slug>[\w\-]+)/$',views.student_submission,name = 'submission'),
   url(r'^create_template/$',views.create_template, name = 'create_template'),]
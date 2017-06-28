from django.conf.urls import url
from perspectivesx import views

urlpatterns = [
   url(r'^add_activity', views.add_activity, name='add_activity'),
   url(r'^$',views.index, name = 'index'),
]
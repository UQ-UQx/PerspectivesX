from django.conf.urls import url
from .views import add_activity, index, student_submission, create_template, curate_item, LTIindex, LTInot_authorized,UserSubmissionItemList,UserCuratedItemList

urlpatterns = [
    url(r'^add_activity/$', add_activity, name='add_activity'),
    url(r'^$', index, name='index'),
    url(r'^get_user_submission_items/$',UserSubmissionItemList.as_view(), name = "REST_user_sub_items"),
    url(r'^get_user_curated_items/$',UserCuratedItemList.as_view(),name = "REST_user_cur_items"),
    url(r'^LTI/$',LTIindex,name = 'LTIindex'),
    url(r'^not_authorized', LTInot_authorized,name = 'LTInot_authorized'),
    url(r'^submission/(?P<activity_name_slug>[\w\-]+)/$', student_submission, name='submission'),
    url(r'^submission/(?P<activity_name_slug>[\w\-]+)/(?P<perspective>\d+)/$', student_submission,
        name="Defined submission"),
    url(r'^create_template/$', create_template, name='create_template'),
    url(r'^curate/(?P<activity_name_slug>[\w\-]+)/$', curate_item, name="Item Curator"),
    url(r'^curate/(?P<activity_name_slug>[\w\-]+)/(?P<item>\d+)/$', curate_item, name="Defined Item Curator")]

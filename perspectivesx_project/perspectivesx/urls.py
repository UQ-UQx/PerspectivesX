from django.conf.urls import url
from .views import add_activity, index, student_submission, create_template, curate_item, LTIindex, LTInot_authorized, \
    UserSubmissionItemList, UserCuratedItemList, PerspectiveList, display_perspective_items, ActivityList, \
    delete_submission_item, delete_curated_item, add_submission_item

urlpatterns = [
    url(r'^add_activity/$', add_activity, name='add_activity'),
    url(r'^$', index, name='index'),
    url(r'^get_user_submission_items/(?P<activity>\d+)/(?P<perspective>\d+)/$', UserSubmissionItemList.as_view(),
        name="REST_user_sub_items"),
    url(r'^display_perspective_items/(?P<activity>\d+)/(?P<perspective>\d+)/$', display_perspective_items,
        name="display_perspective_items"),
    url(r'^get_user_curated_items/(?P<activity>\d+)/(?P<perspective>\d+)/$', UserCuratedItemList.as_view(),
        name="REST_user_cur_items"),
    url(r'^get_template_items/(?P<activity>\d+)/$', PerspectiveList.as_view(), name="REST_template_items"),
    url(r'^get_activities', ActivityList.as_view(), name="REST_activity_list"),
    url(r'^LTI/$', LTIindex, name='LTIindex'),
    url(r'^not_authorized', LTInot_authorized, name='LTInot_authorized'),
    url(r'^submission/(?P<activity_name_slug>[\w\-]+)/$', student_submission, name='submission'),
    url(r'^submission/(?P<activity_name_slug>[\w\-]+)/(?P<perspective>\d+)/$', student_submission,
        name="Defined submission"),
    url(r'^create_template/$', create_template, name='create_template'),
    url(r'^curate/(?P<activity_name_slug>[\w\-]+)/$', curate_item, name="Item Curator"),
    url(r'^curate/(?P<activity_name_slug>[\w\-]+)/(?P<item>\d+)/$', curate_item, name="Defined Item Curator"),
    url(r'delete_submission_item/(?P<item_id>\d+)/$', delete_submission_item, name="delete item"),
    url(r'delete_curated_item/(?P<item_id>\d+)/$', delete_curated_item, name="delete curated item"),
    url(r'add_submission_item/(?P<activity_id>\d+)/(?P<perspective_id>\d+)/(?P<position>\d+)/(?P<item>[\w\ ]+)/$', add_submission_item,
        name="add submission item")]

from django.conf.urls import url

from perspectivesx.views import add_activity, index, student_submission, create_template, curate_item, LTIindex, LTInot_authorized, \
    UserSubmissionItemList, UserCuratedItemList, PerspectiveList, display_perspective_items, \
    GetSubmissionScore, LTItest, studentview

urlpatterns = [
                  url(r'^LTItest/$', LTItest, name='LTItest'),
                  url(r'^LTI/$', LTIindex, name='LTIindex'),
                  url(r'^studentview/(?P<resource_link_id>[\w\-\.]+)/$', studentview, name='studentview'),
                  url(r'^add_activity/(?P<resource_link_id>[\w\-\.]+)/$', add_activity, name='add_activity'),
                  url(r'^$', index, name='index'),
                  url(r'^get_user_submission_items/(?P<activity>\d+)/(?P<perspective>\d+)/(?P<username>[\w\-\.\:]+)/$',
                      UserSubmissionItemList.as_view(),
                      name="REST_user_sub_items"),
                  url(r'^display_perspective_items/(?P<activity>\d+)/(?P<perspective>\d+)/(?P<resource_link_id>[\w\-\.]+)/$', display_perspective_items,
                      name="display_perspective_items"),
                  url(r'^get_user_curated_items/(?P<activity>\d+)/(?P<perspective>\d+)/(?P<username>[\w\-\.\:]+)/$',
                      UserCuratedItemList.as_view(),
                      name="REST_user_cur_items"),
                  url(r'^get_template_items/(?P<activity>\d+)/$', PerspectiveList.as_view(),
                      name="REST_template_items"),
                  url(r'^LTI/$', LTIindex, name='LTIindex'),
                  url(r'^not_authorized', LTInot_authorized, name='LTInot_authorized'),
                  url(r'^submission/(?P<resource_link_id>[\w\-\.]+)/(?P<activity_id>\d+)/$', student_submission, name='submission'),
                  url(r'^submission/(?P<resource_link_id>[\w\-\.]+)/(?P<activity_id>\d+)/(?P<perspective>\d+)/$', student_submission,
                      name="Defined submission"),
                  url(r'^create_template/$', create_template, name='create_template'),
                  url(r'^curate/(?P<activity_name_slug>[\w\-]+)/$', curate_item, name="Item Curator"),
                  url(r'^curate/(?P<activity_name_slug>[\w\-]+)/(?P<item>\d+)/$', curate_item,
                      name="Defined Item Curator"),
                  url(r'GetSubmissionScore/(?P<submission>\d+)/$', GetSubmissionScore.as_view(),
                      name="get_submission"), ]

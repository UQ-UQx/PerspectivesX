from django.conf.urls import url,include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from .views import TemplateViewSet,TemplateItemViewSet,ActivityViewSet,LearnerSubmissionItemViewSet,LearnerSubmissionViewSet,CuratedItemViewSet,SubmissionScoreViewSet

router = routers.DefaultRouter()

router.register(r'Template',TemplateViewSet)
router.register(r'TemplateItem',TemplateItemViewSet)
router.register(r'Activity',ActivityViewSet)
router.register(r'LearnerSubmissionItem',LearnerSubmissionItemViewSet)
router.register(r'LearnerPerspectiveSubmission',LearnerSubmissionViewSet)
router.register(r'CuratedItem',CuratedItemViewSet)
router.register(r'SubmissionScore',SubmissionScoreViewSet)

schema_view = get_swagger_view(title='PerspectivesX API')

urlpatterns = [
    url(r'^docs/', schema_view),
]
urlpatterns += router.urls

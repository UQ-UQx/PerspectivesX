from django.db import models

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Template(models.Model):
    '''
    Model for PerspectivesX Template.
    '''
    name = models.CharField(max_length=5000, blank=False, verbose_name="Template Name")
    description = models.TextField(blank=False)

class TemplateItem(models.Model):
    '''
    Model for PerspectivesX Template Item.
    '''
    name = models.CharField(max_length=5000, blank=False, verbose_name="Item Name")
    description = models.TextField(blank=False)
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    template = models.ForeignKey(Template)

class Activity(models.Model):
    '''
    Model for Acitivy that uses a PerspectivesX Template.
    '''
    name = models.CharField(max_length=5000, blank=False, verbose_name="Activity Name")
    description = models.TextField(blank=False)

    template = models.ForeignKey(Template)

    SELECTED = 'Learner Selected'
    RANDOM = 'Randomly Assigned'
    ALL = 'Learner Completes All Perspectives'
    PERSPECTIVE_SELECTION_OPTIONS = (
            (SELECTED, SELECTED),
            (RANDOM, RANDOM),
            (ALL, ALL)
    )
    perspective_selection = models.CharField(max_length=100, choices=PERSPECTIVE_SELECTION_OPTIONS, default=ASSIGNED)

    enable_curation = models.BooleanField(blank=False, default=True)
    view_knowledge_base_before_sumbmission = models.BooleanField(blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class LearnerSubmission(models.Model):
    '''
    Model for a Learner Submission for a PerpectivesX Activity.
    '''
    item = models.CharField(max_length=5000, blank=False, verbose_name="Item Name")
    description = models.TextField(blank=True)
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    template_item = models.ForeignKey(TemplateItem)
    activity = models.ForeignKey(Activity)

    NOSHARE = "Don't Share"
    ANON = 'Share Anonymously'
    SHARE = 'Share with other learners'
    SHARE_OPTIONS = (
            (SELECTED, SELECTED),
            (RANDOM, RANDOM),
            (ALL, ALL)
    )
    sharing = models.CharField(max_length=100, choices=SHARE_OPTIONS, default=SHARE)

    created_by = models.OneToOneField(User)
    created_at = models.DateTimeField(auto_now_add=True)

class LearnerPerspective(models.Model):
    '''
    Model to store how a learner is assigned to a particular perspective.
    '''

    template_item = models.ForeignKey(TemplateItem)
    activity = models.ForeignKey(Activity)

    SELECTED = "Learner Selected"
    RANDOM = 'Randomly Assigned'
    ALL = 'Assigned'
    PERSPECTIVE_SELECTION_OPTIONS = (
            (SELECTED, SELECTED),
            (RANDOM, RANDOM),
            (ALL, ALL)
    )
    perspective_selection = models.CharField(max_length=100, choices=PERSPECTIVE_SELECTION_OPTIONS, default=SELECTED)
    created_at = models.DateTimeField(auto_now_add=True)

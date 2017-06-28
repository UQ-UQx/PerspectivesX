from django.db import models

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Template(models.Model):
    '''
    Model for PerspectivesX Template.
    '''
    name = models.CharField(max_length=5000, blank=False, verbose_name="Template Name")
    description = models.TextField(blank=False)

    def __unicode__(self):
        return self.name

class TemplateItem(models.Model):
    '''
    Model for PerspectivesX Template Item.
    '''
    name = models.CharField(max_length=5000, blank=False, verbose_name="Item Name")
    description = models.TextField(blank=False)
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    template = models.ForeignKey(Template)

    def __unicode__(self):
        return self.name

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
    perspective_selection = models.CharField(max_length=100, choices=PERSPECTIVE_SELECTION_OPTIONS, default=RANDOM)


    enable_curation = models.BooleanField(blank=False, default=True)
    view_knowledge_base_before_sumbmission = models.BooleanField(blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class LearnerSubmissionItem(models.Model):
    '''
    Model for a Learner Submission Item for a PerpectivesX Activity.
    '''

    # Stores the item entry from the user
    item = models.CharField(max_length=5000, blank=False, verbose_name="Item Name")

    #description might not be relevant anymore.
    description = models.TextField(blank=True)

    # Position of item in learner submission
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    template_item = models.ForeignKey(TemplateItem)
    activity = models.ForeignKey(Activity)

    created_by = models.OneToOneField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "item number".format(self.position)

class LearnerPerspectiveSubmission(models.Model):
    '''
    Model to store how a learner submission is assigned to a particular perspective.
    '''

    template_item = models.ForeignKey(TemplateItem)
    activity = models.ForeignKey(Activity)

    # Define selection mode
    SELECTED = "Learner Selected"
    RANDOM = 'Randomly Assigned'
    ALL = 'Assigned'
    PERSPECTIVE_SELECTION_OPTIONS = (
            (SELECTED, SELECTED),
            (RANDOM, RANDOM),
            (ALL, ALL)
    )

    #Define share mode
    NOSHARE = "Don't Share"
    ANON = 'Share Anonymously'
    SHARE = 'Share with other learners'
    SHARE_OPTIONS = (
            (NOSHARE,NOSHARE),
            (ANON, ANON),
            (SHARE, SHARE)
    )

    sharing = models.CharField(max_length=100, choices=SHARE_OPTIONS, default=SHARE)
    perspective_selection = models.CharField(max_length=100, choices=PERSPECTIVE_SELECTION_OPTIONS, default=SELECTED)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Template(models.Model):
    '''
    Model for PerspectivesX Template.
    A Template is a associated with an activity and defines the actions required from the learner
    '''
    name = models.CharField(max_length=5000,verbose_name="Template Name")
    description = models.TextField()

    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Templates"

class TemplateItem(models.Model):
    '''
    Model for PerspectivesX Template Item.
    Template Items are the possible perspectives associated with a template
    '''
    name = models.CharField(max_length=5000,verbose_name="Item Name")
    # description = models.TextField(blank=False) not too sure if this is needed
    color = models.CharField(max_length = 7,default = "#ff0000")
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    template = models.ForeignKey(Template)

    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["template","position"]
        verbose_name_plural = "Template Items"

class Activity(models.Model):
    '''
    Model for Acitivy that uses a PerspectivesX Template.
    An activity is created by a teacher. It is based on a pre-existing or a newly defined activity template
    The Teacher defines:
    Title,
    Description,
    How perspectives are assigned to learners
    How curations of perspective is assigned to learners
    Knowledge base settings for the activity
    Contribution Scre / Curation score
    Minimum contribution/Curated responses
    '''
    title = models.CharField(max_length=5000, blank=False, verbose_name="Activity Name")
    description = models.TextField(blank=False)
    slug = models.SlugField()
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

    SELECTED = 'Allow learners to choose a perspective to curate'
    RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
    ALL = 'Allow Learners to curate all perspectives'
    PERSPECTIVE_CURATION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )

    enable_curation = models.CharField(max_length=100, choices=PERSPECTIVE_CURATION_OPTIONS, default=RANDOM)
    view_knowledge_base_before_sumbmission = models.BooleanField(blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    contribution_score = models.IntegerField(default = 50)
    curation_score = models.IntegerField(default =50)
    minimum_contribution = models.IntegerField(default = 3)
    minimum_curation = models.IntegerField(default = 3)



    def save(self,*args,**kwargs):
        self.slug = slugify(self.title)
        super(Activity,self).save(*args,**  kwargs)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["template", "title"]
        verbose_name_plural = "Activities"

class LearnerPerspectiveSubmission(models.Model):
    '''
    Model to store how a learner submission is assigned to a particular perspective.
    '''
    #selected_perspective is the perspective selected by the learner
    selected_perspective = models.ForeignKey(TemplateItem)
    #Activity undertaken by the learner
    activity = models.ForeignKey(Activity)

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
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return "{} Submission from {}".format(self.activity.title, self.created_by.username)

    class Meta:
        ordering = ["activity","created_by"]
        verbose_name_plural = "Learner Submissions"
        unique_together = ('activity','created_by' )

class LearnerSubmissionItem(models.Model):
    '''
    Model for a Learner Submission Item for a PerpectivesX Activity.
    '''

    # Stores the item entry from the user
    item = models.CharField(max_length=5000, blank=False, verbose_name="Item Name")

    # Position of item in learner submission
    position = models.PositiveSmallIntegerField(blank=True, null=True)

    learner_submission = models.ForeignKey(LearnerPerspectiveSubmission)

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Item number {} at {}".format(self.position, self.learner_submission)

    class Meta:
        ordering = ["learner_submission","position"]
        verbose_name_plural = "Learner Submission Items"

class CuratedItem(models.Model):
    item = models.ForeignKey(LearnerSubmissionItem)
    score = models.IntegerField()
    curator = models.ForeignKey(User)

    def __unicode__(self):
        return " {}. Curated by {}".format(self.item, self.curator)


class SubmissionScore(models.Model):
    submission = models.ForeignKey(LearnerPerspectiveSubmission)
    participation_grade = models.IntegerField()
    curation_grade = models.IntegerField()
    total_grade = models.IntegerField()

    def __unicode__(self):
        return "{} \n Grades: \n Contribution: {}\n Curation: {} \n Total: {} \n".format(
            self.submission, self.participation_grade, self.curation_grade, self.total_grade)



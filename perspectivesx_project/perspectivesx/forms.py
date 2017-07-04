from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Row,Hidden
from crispy_forms.bootstrap import FormActions,InlineRadios,PrependedText, InlineField,StrictButton
from models import Template, TemplateItem, Activity, LearnerPerspectiveSubmission,LearnerSubmissionItem,User
from formsetlayout import Formset as FormSetLayout

class ActivityForm(forms.ModelForm):


    title = forms.CharField(max_length = 5000, label= "Title:")
    description = forms.CharField(label = "Decription:", widget= forms.Textarea)
    template = forms.ModelChoiceField(queryset = Template.objects.all() ,label= "Choose activity template:")

    SELECTED = 'Allow learners to choose a perspective'
    RANDOM = 'Randomly assign a perspective for learner'
    ALL = 'Allow Learners to contribute to all perspectives'
    PERSPECTIVE_SELECTION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    learner_contribution = forms.ChoiceField(choices = PERSPECTIVE_SELECTION_OPTIONS, label= "Learner Contribution:",
                                             widget= forms.RadioSelect)

    SELECTED = 'Allow learners to choose a perspective to curate'
    RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
    ALL = 'Allow Learners to curate all perspectives'
    PERSPECTIVE_CURATION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    learner_curation = forms.ChoiceField(choices=PERSPECTIVE_CURATION_OPTIONS, label= "Learner Curation:",
                                         widget= forms.RadioSelect)

    ENABLE = 'Enable Search'
    SUMMARIZE = 'Use Topic Models to summarise learner submissions'
    VIEW = 'Allow learners to view the knowledge base before making a submission'
    KB_SETTINGS_OPTIONS = (
        (ENABLE, ENABLE),
        (SUMMARIZE, SUMMARIZE),
        (VIEW, VIEW)
    )
    kb_setting = forms.ChoiceField(choices =KB_SETTINGS_OPTIONS, label= "Kwowledge Base Setting:",
                                   widget=forms.RadioSelect)
    contribution_score = forms.IntegerField(label ="Contribution Score", initial = 50)
    curation_score = forms.IntegerField(label= "Curation Score", initial = 50)
    minimum_contributions = forms.IntegerField(label= "Minimum Contributions", initial = 3 )
    minimum_curations = forms.IntegerField(label = "Minimum Curated Response", initial = 3)

    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = '/perspectivesX/add_activity/'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class ='col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        self.helper.layout = Layout(
            Fieldset(
            "",'title','description','template',
            FormActions(
                HTML("OR &emsp; "),
                StrictButton("Create Custrom Template", name="create template",
                            value="create template",css_class= 'create-template')),
           'learner_contribution','learner_curation','kb_setting',
            PrependedText('contribution_score', '%', active=True),
            PrependedText('curation_score','%',active= True),'minimum_contributions','minimum_curations'
             ),
            FormActions(
                Submit('Add Activity', 'Add Activity')
            )
        )



    class Meta:
        #associate activity Form with an Activity
        model = Activity
        fields= ('title','description','template','learner_contribution','learner_curation','kb_setting',
                 'contribution_score','curation_score','minimum_contributions','minimum_curations')

class LearnerSubmissionItemForm(forms.ModelForm):
    #Item stores the learner's contribution (entry) for this Item
    item = forms.CharField(label ="")
    #Position stores the position of the item (index of the contribution)
    position = forms.IntegerField(widget = forms.HiddenInput, required = False)
    #learner_submission maps the item to the relevant learner submission
    learner_submission = forms.ModelChoiceField(queryset = LearnerPerspectiveSubmission.objects.all(),
                                                widget = forms.HiddenInput, required = False)

    def __init__(self,*args,**kwargs):
        super(LearnerSubmissionItemForm, self).__init__(*args, **kwargs)
        #Define form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('','item','position','learner_submission'))

    class Meta:
        model = LearnerSubmissionItem
        fields = ('item','position','learner_submission')


class LearnerForm(forms.ModelForm):
    #perspective_selection stores the perspective choosen by the learner
    selected_perspective = forms.ModelChoiceField(queryset=[], label = 'Choose a perspective')

    NOSHARE = "Don't Share"
    ANON = 'Share Anonymously'
    SHARE = 'Share with other learners'
    SHARE_OPTIONS = (
        (NOSHARE, NOSHARE),
        (ANON, ANON),
        (SHARE, SHARE)
    )
    #sharing stores the share mode selected by the user
    sharing = forms.ChoiceField(choices = SHARE_OPTIONS ,label = 'Privacy Settings')
    #activity maps the submission to the undertaken activity
    activity = forms.ModelChoiceField(queryset=Activity.objects.all(),widget = forms.HiddenInput)
    created_by = forms.ModelChoiceField(queryset = User.objects.all(),
                                        initial = User.objects.get(username = 'marcolindley'), widget = forms.HiddenInput)

    def __init__(self,*args, **kwargs):

        #retrive args from kwargs array
        self.template_name = kwargs.pop('template_name')
        self.activity = kwargs.pop('activity')
        # call super.__init__()
        super(LearnerForm, self).__init__(*args, **kwargs)

        self.fields['selected_perspective']  = forms.ModelChoiceField(queryset=TemplateItem.objects.filter(
            template = Template.objects.filter(name= self.template_name)),
            label="Choose a perspective:", widget = forms.RadioSelect, empty_label= None)
        self.fields['activity'].initial = self.activity
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        self.helper.layout = Layout(
            Fieldset('Submission',
               InlineRadios('selected_perspective'),FormSetLayout('formset'),InlineRadios('sharing'),
                     'activity'
            ),
            FormActions(
                Submit("Save","Save"),Submit('Submit', 'Submit'),
            )
        )
    class Meta:
        model = LearnerPerspectiveSubmission
        fields = ('selected_perspective','sharing','activity','created_by')



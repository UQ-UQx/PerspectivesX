from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field, Row,Hidden
from crispy_forms.bootstrap import FormActions,InlineRadios,PrependedText, InlineField,StrictButton
from perspectivesx.models import Template, TemplateItem, Activity, LearnerPerspectiveSubmission,LearnerSubmissionItem,User,CuratedItem
from perspectivesx.formsetlayout import Formset as FormSetLayout

class ActivityForm(forms.ModelForm):

    title = forms.CharField(max_length = 5000, label= "Title:")
    description = forms.CharField(label = "Decription:", widget= forms.Textarea)

    perspective_terminology = forms.CharField(max_length = 1000, label= "Perspective Terminology:")
    item_terminology = forms.CharField(max_length = 1000, label= "Item Terminology:")

    template = forms.ModelChoiceField(queryset = Template.objects.all() ,label= "Choose activity template:")

    SELECTED = 'Allow learners to choose a perspective'
    RANDOM = 'Randomly assign a perspective for learner'
    ALL = 'Allow Learners to contribute to all perspectives'
    PERSPECTIVE_SELECTION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    perspective_selection = forms.ChoiceField(choices = PERSPECTIVE_SELECTION_OPTIONS, label= "Learner Contribution:",
                                             widget= forms.RadioSelect)

    '''
    SELECTED = 'Allow learners to choose a perspective to curate'
    RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
    ALL = 'Allow Learners to curate all perspectives'
    PERSPECTIVE_CURATION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    enable_curation = forms.ChoiceField(choices=PERSPECTIVE_CURATION_OPTIONS, label= "Learner Curation:",
                                         widget= forms.RadioSelect)

    ENABLE = 'Enable Search'
    SUMMARIZE = 'Use Topic Models to summarise learner submissions'
    VIEW = 'Allow learners to view the knowledge base before making a submission'
    KB_SETTINGS_OPTIONS = (
        (ENABLE, ENABLE),
        (SUMMARIZE, SUMMARIZE),
        (VIEW, VIEW)
    )
    kb_setting = forms.ChoiceField(choices =KB_SETTINGS_OPTIONS, label= "Knowledge Base Setting:",
                                   widget=forms.RadioSelect)
    '''

    view_knowledge_base_before_sumbmission = forms.BooleanField(label ="Allow learners to view Knowledge base before submission", initial = False)
    enable_search = forms.BooleanField(label ="Enable search", initial = False)

    contribution_score = forms.IntegerField(label ="Contribution Score", initial = 50)
    curation_score = forms.IntegerField(label= "Curation Score", initial = 50)
    minimum_contributions = forms.IntegerField(label= "Minimum Number of Contributions", initial = 3 )
    minimum_curations = forms.IntegerField(label = "Minimum Number of Curated Responses", initial = 3)

    def __init__(self, *args, **kwargs):
        resource_link_id = "-"
        if 'resource_link_id' in kwargs:
            resource_link_id = kwargs.pop('resource_link_id')
        super(ActivityForm, self).__init__(*args, **kwargs)
        activity_id = "-"
        if 'instance' in kwargs:
            activity = kwargs['instance']
            activity_id = activity.id
            #print(activity_id)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = '/perspectivesX/add_activity/'+resource_link_id+'/'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class ='col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        self.helper.layout = Layout(
            HTML('<div class="form-group"><label class="control-label control-label col-sm-2">Activity ID:</label><div class="controls col-sm-10">' + str(activity_id) + '</div></div>'),
            Fieldset(
            "",'title','description','template',
            FormActions(
                HTML("OR &emsp; "),
                StrictButton("Create Custom Template", name="create template",
                            value="create template",css_class= 'create-template')),
           'perspective_selection','view_knowledge_base_before_sumbmission','enable_search','perspective_terminology', 'item_terminology',
            PrependedText('contribution_score', '%', active=True),
            PrependedText('curation_score','%',active= True),'minimum_contributions','minimum_curations'
             ),
            FormActions(
                Submit('Save', 'Save')
            )
        )

    class Meta:
        #associate activity Form with an Activity
        model = Activity
        fields= ('title','description','perspective_terminology', 'item_terminology', 'template','perspective_selection','view_knowledge_base_before_sumbmission','enable_search',
                 'contribution_score','curation_score','minimum_contributions','minimum_curations')

class LearnerSubmissionItemForm(forms.ModelForm):
    #Item stores the learner's contribution (entry) for this Item
    item = forms.CharField(label="")
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

class AddLearnerSubmissionItemForm(forms.ModelForm):
    # Item stores the learner's contribution (entry) for this Item
    item = forms.CharField(label="")
    # Position stores the position of the item (index of the contribution)
    position = forms.IntegerField(widget=forms.HiddenInput, required=False)
    # learner_submission maps the item to the relevant learner submission
    learner_submission = forms.ModelChoiceField(queryset=LearnerPerspectiveSubmission.objects.all(),
                                                widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super(AddLearnerSubmissionItemForm, self).__init__(*args, **kwargs)
        # Define form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset('Enter Item', 'item', 'position', 'learner_submission'),  FormActions(
                Submit('Submit', 'Submit')
            ))

    class Meta:
        model = LearnerSubmissionItem
        fields = ('item', 'position', 'learner_submission')

class LearnerForm(forms.ModelForm):
    #perspective_selection stores the perspective choosen by the learner
    selected_perspective = forms.ModelChoiceField(queryset=[])

    NOSHARE = "Don't Share"
    ANON = 'Share Anonymously'
    SHARE = 'Share with other learners'
    SHARE_OPTIONS = (
        (SHARE, SHARE),
        (ANON, ANON),
        (NOSHARE, NOSHARE),
    )
    #sharing stores the share mode selected by the user
    sharing = forms.ChoiceField(choices = SHARE_OPTIONS ,label = 'Privacy Settings', initial="Share with other learners")
    #activity maps the submission to the undertaken activity
    activity = forms.ModelChoiceField(queryset=Activity.objects.all(),widget = forms.HiddenInput)
    #maps the submission to a particular user; TO BE UPDATED WITH LTI INFO
    created_by = forms.ModelChoiceField(queryset = User.objects.all(), widget = forms.HiddenInput)

    def __init__(self,*args, **kwargs):

        #retrive args from kwargs array
        # self.template_name = kwargs.pop('template_name')
        self.activity = kwargs.pop('activity')
        self.user = kwargs.pop('user')
        self.perspective = kwargs.pop('perspective')
        # call super.__init__()
        super(LearnerForm, self).__init__(*args, **kwargs)

        #set the hidden field values with given parameters
        self.fields['selected_perspective']  = forms.ModelChoiceField(queryset=TemplateItem.objects.filter(
            id = self.perspective), initial = self.perspective, widget = forms.HiddenInput, empty_label= None)

        self.fields['activity'].initial = self.activity
        self.fields['created_by'].initial = User.objects.get(username = self.user)

        #define form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'

        #get selected perspective title
        selected_perspective = TemplateItem.objects.get(id = self.perspective).name
        #define form layout

        self.helper.layout = Layout(

            Fieldset('Your initial contributions:',
               HTML("<strong>Please submit items for:</strong> " + selected_perspective),
               InlineRadios('selected_perspective'),FormSetLayout('formset',header = "Add signposts:"),InlineRadios('sharing'),
                     'activity','created_by'
            ),
            FormActions(
                Submit('Submit', 'Submit'),
            )
        )

    class Meta:
        model = LearnerPerspectiveSubmission
        fields = ('selected_perspective','sharing','activity','created_by')

class TemplateItemForm(forms.ModelForm):
    name = forms.CharField(max_length= 500, label = 'Name:', initial = "Perspective/Dimension Name")
    color = forms.CharField(max_length= 7, label = "Color: ", required = False,
                            widget= forms.TextInput(attrs = {'type': 'color', 'style': 'width: 10%  '}))
    icon_small = forms.CharField(max_length=1000, label = 'Small Icon', initial = "/path/to/iconsm.png")
    icon_large = forms.CharField(max_length=1000, label = 'Large Icon', initial = "/path/to/iconlg.png")
    position = forms.IntegerField(widget = forms.HiddenInput, required = False)
    template = forms.ModelChoiceField(queryset= [],widget= forms.HiddenInput, required = False)


    def __init__(self,*args,**kwargs):
        super(TemplateItemForm, self).__init__(*args, **kwargs)
        #Define form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Fieldset('Perspective/Dimension:','name','color', 'icon_small', 'icon_large', 'position','template'))
    class Meta:
        model = TemplateItem
        fields = ('name','color','icon_small', 'icon_large', 'position', 'template')


class TemplateCreatorForm(forms.ModelForm):
    #define main fields: template name & description
    name = forms.CharField( label= "Template Title:", initial = "\"Template Name\"")
    description = forms.CharField(label = "Descritpion: ", widget = forms.Textarea, initial = "Describe the activity Template")
    #icon = forms.ImageField()
    def __init__(self, *args, **kwargs):
        # call super.__init__()
        super(TemplateCreatorForm, self).__init__(*args, **kwargs)
        # define form helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        # define form layout
        '''
        self.helper.layout = Layout(
            Fieldset('','name','description','icon',
                    FormSetLayout('formset', header="Multi-Perspective Fieldset", item = "Perspective")),
            FormActions(
                Submit("Save", "Save")
            )
        )
        '''

        self.helper.layout = Layout(
            Fieldset('','name','description',
                    FormSetLayout('formset', header="Multi-Perspective Fieldset", item = "Perspective")),
            FormActions(
                Submit("Save", "Save")
            )
        )

    class Meta:
        model = Template
        fields = ('name','description')

class ItemCuratorForm(forms.ModelForm):
    item = forms.ModelChoiceField(queryset= [], widget = forms.HiddenInput)
    comment = forms.CharField(required = False)
    curator = forms.ModelChoiceField(queryset=[], widget = forms.HiddenInput)

    def __init__(self,*args, **kwargs):
        #retrieve args from kwargs
        self.item= kwargs.pop("item")
        self.curator = kwargs.pop("curator")
        #call super
        super(ItemCuratorForm,self).__init__(*args,**kwargs)
        #define fields item and curator and set heir values
        self.fields['item'] = forms.ModelChoiceField(queryset= LearnerSubmissionItem.objects.filter(id = self.item),
                                                     initial = self.item, widget = forms.HiddenInput)
        self.fields['curator'] = forms.ModelChoiceField(queryset = User.objects.filter(username = self.curator),
                                                        initial = User.objects.get(username = self.curator) , widget= forms.HiddenInput)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        # define form layout
        self.helper.layout = Layout(
            Fieldset('Curation', 'comment', 'item','curator'),
            FormActions(
                Submit("Submit", "Submit")
            )
        )

    class Meta:
        model = CuratedItem
        fields = ('item', 'comment','curator')

class ItemChooseForm(forms.Form):
    item = forms.ModelChoiceField(queryset = [])

    def __init__(self,*args,**kwargs):
        self.queryset = kwargs.pop('queryset')
        self.item = kwargs.pop('item')
        # self.activity = kwargs.pop('activity')
        # self.all = kwargs.pop('all')
        # self.curator = kwargs.pop('curator')
        # call super
        super(ItemChooseForm, self).__init__(*args, **kwargs)
        # define fields item and curator and set heir values
        # if(self.all):
        #     #retrive all LearnerSubmissionItems from activity
        #     # !!!!!!!!!!!!!!!! UPDATE TO EXCLUDE items from curator once LTI is set up !!!!!!!!!!!
        #     learner_submission_items = LearnerSubmissionItem.objects.filter(learner_submission__activity= self.activity)
        #     #retirve items already curated
        #     items_already_curated = CuratedItem.objects.filter(curator = self.curator).filter(item__in = learner_submission_items )
        #     #retrieve actual items from curated items
        #     items = LearnerSubmissionItem.objects.filter(id__in = items_already_curated.values('item_id'))
        #     #retrieve learner submission from actual items
        #     submissions = LearnerPerspectiveSubmission.objects.filter(id__in = items.values('learner_submission_id'))
        #     #retrieve perspectives from submissions
        #     perspectives_already_curated = TemplateItem.objects.filter(id__in = submissions.values('selected_perspective_id'))
        #
        #     self.fields['item'] = forms.ModelChoiceField(queryset=LearnerSubmissionItem.objects.filter(
        #         learner_submission=LearnerPerspectiveSubmission.objects.filter(activity=self.activity).exclude(selected_perspective__in= perspectives_already_curated)))
        # else:
        #
        #
        #     # !!!!!!!!!!! UPDATE TO EXCLUDE items from curator once LTI user is set up !!!!!!!!!!!!!!!
        # self.fields['item']  = forms.ModelChoiceField(queryset = LearnerSubmissionItem.objects.filter(
        #     learner_submission= LearnerPerspectiveSubmission.objects.filter(activity=self.activity)))
        self.fields['item'] = forms.ModelChoiceField(queryset=self.queryset)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = 'col-sm-10'
        self.helper.label_class = 'control-label col-sm-2'
        # define form layout
        self.helper.layout = Layout(
            Fieldset('Choose scenario', 'item'),
            FormActions(
                Submit("Continue", "Continue")
            )
        )

class deleteForm( forms.Form):
    CHOICES= (
        (True, "Yes"),
        (False, "No"),
    )
    choice  = forms.ChoiceField(choices= CHOICES)

    def __init__(self, *args, **kwargs):
        super(deleteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = "form-horizontal"
        self.helper.layout = Layout(
            Fieldset('Comfirm ?', 'choice'),
            FormActions(
                Submit("Continue", "Continue")
            )
        )

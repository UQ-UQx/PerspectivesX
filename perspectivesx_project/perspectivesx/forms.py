from django import forms
from models import Template, TemplateItem, Activity

class ActivityForm(forms.ModelForm):
    title = forms.CharField(max_length = 5000, help_text= "Title:")
    description = forms.CharField(help_text = "Decription:")
    template = forms.ModelChoiceField(queryset = Template.objects.all() ,help_text= "Activity template:")

    SELECTED = 'Allow learners to choose a perspective'
    RANDOM = 'Randomly assign a perspective for learner'
    ALL = 'Allow Learners to contribute to all perspectives'
    PERSPECTIVE_SELECTION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    learner_contribution = forms.ChoiceField(choices = PERSPECTIVE_SELECTION_OPTIONS, help_text= "Learner Contribution:",
                                             widget= forms.RadioSelect)

    SELECTED = 'Allow learners to choose a perspective to curate'
    RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
    ALL = 'Allow Learners to curate all perspectives'
    PERSPECTIVE_CURATION_OPTIONS = (
        (SELECTED, SELECTED),
        (RANDOM, RANDOM),
        (ALL, ALL)
    )
    learner_curation = forms.ChoiceField(choices=PERSPECTIVE_CURATION_OPTIONS, help_text= "Learner Curation:",
                                         widget= forms.RadioSelect)

    ENABLE = 'Enable Search'
    SUMMARIZE = 'Use Topic Models to summarise learner submissions'
    VIEW = 'Allow learners to view the knowledge base before making a submission'
    KB_SETTINGS_OPTIONS = (
        (ENABLE, ENABLE),
        (SUMMARIZE, SUMMARIZE),
        (VIEW, VIEW)
    )
    kb_setting = forms.ChoiceField(choices =KB_SETTINGS_OPTIONS, help_text= "Kwowledge Base Setting:",
                                   widget=forms.RadioSelect)

    class Meta:
        #associate activity Form with an Activity
        model = Activity
        fields= ('title','description','template','learner_contribution','learner_curation','kb_setting')


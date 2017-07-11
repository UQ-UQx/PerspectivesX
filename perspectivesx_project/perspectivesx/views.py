from django.shortcuts import render
from django.http import HttpResponse
from forms import ActivityForm,LearnerForm,LearnerSubmissionItemForm,TemplateCreatorForm,TemplateItemForm
from functools import partial, wraps
from django.forms import modelformset_factory, formset_factory
from models import Activity,Template,TemplateItem, LearnerSubmissionItem, LearnerPerspectiveSubmission,User
# import pdb; pdb.set_trace()

"""
IN THIS DOCUMENT REPLACE "marcolindley" with LTI user information.
"""

def index(request):
    """
    Defines view for the home page.
    At the moment just some text wiht link to add activity page
    :param request:
    :return:
    """
    return render(request, 'index.html')

def add_activity(request):
    """
    defines view for add activity page
    Shows the add activity form
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save(commit =True)
            return index(request)
        else:
            print form.errors
    else:
        form = ActivityForm()

    return render(request, 'add_activity.html', {'form': form})

def student_submission(request,activity_name_slug):
    """
    View for student submission page
    Displays the submission form in function of the undertaken activity
    :param request: Django HTmlrequest
    :param activity_name_slug: slug name of the activity
    :return:
    """
    #retrieve information from parameter
    activity = Activity.objects.get(slug=activity_name_slug)
    template = Template.objects.get(name=activity.template)
    context_dict = {'activity_name':activity.title }
    #Check wether submission already exists if so set extra =0 otherwise extra = activity.minimum_contribution
    if LearnerPerspectiveSubmission.objects.filter(activity = activity).filter(created_by= User.objects.get(username ='marcolindley'))  .exists():
        extra = 0
    else:
        extra = activity.minimum_contribution



    if request.method == "POST":
        #When form is submited generate the form from the activity and template name
        form = LearnerForm(request.POST, template_name = template.name, activity = activity, user = 'marcolindley' )
        context_dict['form'] = form
        #if form is valid
        if form.is_valid():
            #retrive submission meta
            submission = form.save(commit= True)

            #create formset with relevant information taken from submission meta
            input_form_set = modelformset_factory(LearnerSubmissionItem,form = LearnerSubmissionItemForm,extra = extra)

            formset = input_form_set(request.POST)
            context_dict['formset'] = formset
            # print(formset)
            #if formset is valud
            if formset.is_valid():
                #populate items from form set with correct position and submission info
                items = formset.save(commit = False)
                i = 0
                for item in items:
                    item.position = i
                    item.learner_submission = submission
                    item.save()
                return index(request)

            else:
                #Something went wrong when validating the formset remove the submission
                submission.delete()
                print formset.errors
        else:
            print form.errors
    else:
        context_dict['form'] = LearnerForm(template_name= template.name,activity = activity, user = 'marcolindley')
        input_form_set = modelformset_factory(LearnerSubmissionItem,form = LearnerSubmissionItemForm,extra = extra)
        formset = input_form_set()
        context_dict['formset'] = formset
    return render(request, 'learner_submission.html', context_dict)


def create_template(request):
    context_dict = {}
    if request.method == 'POST':
        form = TemplateCreatorForm(request.POST)
        context_dict['form'] = form
        if form.is_valid():
            #retrive Template meta information
            template = form.save(commit = True)
            #create formset
            input_form_set = modelformset_factory(TemplateItem,form=TemplateItemForm, extra = 2)
            formset = input_form_set(request.POST)
            context_dict['formset'] = formset
            # if formset is valud
            if formset.is_valid():
                # populate items from form set with correct position and submission info
                items = formset.save(commit=False)
                i = 0
                for item in items:
                    item.position = i
                    item.template= template
                    item.save()
                return index(request)
            else:
                #Something went wrong when validating the formset remove the template
                template.delete()
                print formset.errors
        else:
            print form.errors
    else:
        form = TemplateCreatorForm()
        input_form_set = modelformset_factory(TemplateItem,form=TemplateItemForm, extra=2)
        formset = input_form_set()
        context_dict['formset'] = formset
        context_dict['form']= form
    return render(request, 'create_template.html', context_dict)
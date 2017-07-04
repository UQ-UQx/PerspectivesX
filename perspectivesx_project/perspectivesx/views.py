from django.shortcuts import render
from django.http import HttpResponse
from forms import ActivityForm,LearnerForm,LearnerSubmissionItemForm
from functools import partial, wraps
from django.forms import formset_factory
from models import Activity,Template,TemplateItem
# import pdb; pdb.set_trace()

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


    if request.method == "POST":
        #When form is submited generate the form from the activity and template name
        form = LearnerForm(request.POST, template_name = template.name, activity = activity)
        context_dict['form'] = form
        #if form is valid
        if form.is_valid():
            #retrive submission meta
            submission = form.save(commit= True)

            #create formset with relevant information taken from submission meta
            input_form_set = formset_factory(LearnerSubmissionItemForm,extra = 3, max_num = 0)

            formset = input_form_set(request.POST,form_kwargs = {'learner_submission' : submission.id,
                                                         'position' : 0})
            context_dict['formset'] = formset
            # print(formset)
            #if formset is valud
            if formset.is_valid():
                #Save submited items from formset
                formset.save(commit = True)
                return index(request)
            else:
                #Something went wrong when validating the formset remove the submission
                submission.delete()
                print formset.errors
        else:
            print form.errors
    else:
        context_dict['form'] = LearnerForm(template_name= template.name,activity = activity)
        input_form_set = formset_factory(
            wraps(LearnerSubmissionItemForm)(partial(LearnerSubmissionItemForm)), extra=3)
        formset = input_form_set()
        context_dict['formset'] = formset

    return render(request, 'learner_submission.html', context_dict)


def create_template(request):
    pass
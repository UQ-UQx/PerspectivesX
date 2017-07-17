from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from forms import ActivityForm, LearnerForm, LearnerSubmissionItemForm, TemplateCreatorForm, TemplateItemForm, \
    ItemCuratorForm, CurationItemChooseForm
from functools import partial, wraps
from django.forms import modelformset_factory, formset_factory
from models import Activity, Template, TemplateItem, LearnerSubmissionItem, LearnerPerspectiveSubmission, User
from rest_framework import viewsets
from .serializers import *
from random import randint

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
    return render(request, 'index.html', {'activities': Activity.objects.all()})


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
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = ActivityForm()

    return render(request, 'add_activity.html', {'form': form})


def student_submission(request, activity_name_slug, extra=0):
    """
    View for student submission page
    Displays the submission form in function of the undertaken activity
    :param request: Django HTmlrequest
    :param activity_name_slug: slug name of the activity
    :return:
    """
    # retrieve information from parameters
    activity = Activity.objects.get(slug=activity_name_slug)
    template = Template.objects.get(name=activity.template)
    context_dict = {'activity_name': activity.title}
    # retrieve the instance (it might not exists handle with a try except block)
    try:
        instance = LearnerPerspectiveSubmission.objects.filter(activity=activity).get \
            (created_by=User.objects.filter(username='marcolindley'))
    except LearnerPerspectiveSubmission.DoesNotExist:
        instance = None

    # retrive the pre_existing_answers (they might not exists,in which case filter will retunr an empty queryset)
    pre_existing_answers = LearnerSubmissionItem.objects.filter(
        learner_submission=instance)

    # Check wether submission already exists if so set extra =0 otherwise extra = activity.minimum_contribution
    if pre_existing_answers.exists():
        extra = 0
    else:
        extra = activity.minimum_contribution

    # If we get a POST
    if request.method == "POST":
        # check the action, if it contains "add new" we are adding a form to the formset.
        if (request.POST.keys().__contains__('action') and request.POST['action'].__contains__("Add new")):
            # increment extra
            extra = int(request.POST['extra']) + 1
            # define the form and formset
            context_dict['form'] = LearnerForm(template_name=template.name, activity=activity, user='marcolindley',
                                               instance=instance)
            input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm, extra=extra)
            # prepopulate the formset with pre_existing_answers
            formset = input_form_set(queryset=pre_existing_answers)
            context_dict['formset'] = formset

        else:  # When form is submited generate the form from the activity and template name
            form = LearnerForm(request.POST, template_name=template.name, activity=activity, user='marcolindley',
                               instance=instance)
            context_dict['form'] = form
            # if form is valid
            if form.is_valid():
                # retrive submission meta
                submission = form.save(commit=True)

                # create formset with relevant information taken from submission meta
                input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm,
                                                      extra=extra)

                formset = input_form_set(request.POST, queryset=pre_existing_answers)
                context_dict['formset'] = formset
                # print(formset)
                # if formset is valud
                if formset.is_valid():
                    # populate items from form set with correct position and submission info
                    items = formset.save(commit=False)
                    i = 0
                    # adjust position value depending on pre_existing_answers
                    if (pre_existing_answers.exists()):
                        i = pre_existing_answers.count()

                    for item in items:
                        item.position = i
                        i += 1
                        item.learner_submission = submission
                        item.save()

                    # create the Submission score object attached to this submission
                    # participation score = number of submited contribution/activity.minimum_contribution
                    # max score is 100% hence limit i/activity.minimum_contribution to 1
                    participation_score = min(1, i / activity.minimum_contribution) * 100
                    # curation score = number of curated items on this activity by user/ activity.minimum_curation
                    # replace "marcoLindley" with LTI user info
                    curation_score = min(1, CuratedItem.objects.filter(
                        curator=User.objects.get(username="marcolindley")).filter(
                        item=LearnerSubmissionItem.objects.filter(
                            learner_submission=LearnerPerspectiveSubmission.objects.filter(
                                activity=activity))).count() / activity.minimum_curation) * 100

                    total_score = (participation_score * activity.contribution_score / 100) + \
                                  (curation_score * activity.contribution_score / 100)

                    SubmissionScore.objects.create(submission=submission, participation_grade=participation_score,
                                                   curation_grade=curation_score,
                                                   total_grade=total_score)

                    return index(request)

                else:
                    # Something went wrong when validating the formset remove the submission
                    submission.delete()
                    print formset.errors
                    input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm,
                                                          extra=extra)
                    formset = input_form_set(queryset=pre_existing_answers)
                    context_dict['formset'] = formset
            else:
                input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm,
                                                      extra=extra)

                formset = input_form_set(request.POST, queryset=pre_existing_answers)
                context_dict['formset'] = formset
                print form.errors

    else:
        context_dict['form'] = LearnerForm(template_name=template.name, activity=activity, user='marcolindley',
                                           instance=instance)
        input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm, extra=extra)
        formset = input_form_set(queryset=pre_existing_answers)
        context_dict['formset'] = formset
    context_dict['extra'] = extra
    return render(request, 'learner_submission.html', context_dict)


def create_template(request):
    context_dict = {}
    extra = 2
    if request.method == "POST":
        if (request.POST.keys().__contains__('action') and request.POST['action'].__contains__("Add new")):
            # increment extra
            extra = int(request.POST['extra']) + 1
            form = TemplateCreatorForm(request.POST)
            input_form_set = modelformset_factory(TemplateItem, form=TemplateItemForm, extra=extra)

            formset = input_form_set(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                initial = []
                for instance in instances:
                    initial.append({'name': instance.name})
                formset = input_form_set(queryset=TemplateItem.objects.none(), initial=initial)
                context_dict['formset'] = formset
                context_dict['form'] = form
            else:
                print(formset.errors)
        else:
            form = TemplateCreatorForm(request.POST)
            context_dict['form'] = form
            if form.is_valid():
                # retrive Template meta information
                template = form.save(commit=True)
                # create formset
                input_form_set = modelformset_factory(TemplateItem, form=TemplateItemForm, extra=extra)
                formset = input_form_set(request.POST, queryset=TemplateItem.objects.none())
                context_dict['formset'] = formset
                # if formset is valud
                if formset.is_valid():
                    # populate items from form set with correct position and submission info
                    items = formset.save(commit=False)
                    i = 0
                    for item in items:
                        item.position = i
                        item.template = template
                        item.save()
                        i += 1
                    return index(request)
                else:
                    # Something went wrong when validating the formset remove the template
                    template.delete()
                    print formset.errors
            else:
                print form.errors
    else:
        form = TemplateCreatorForm()
        input_form_set = modelformset_factory(TemplateItem, form=TemplateItemForm, extra=extra)
        formset = input_form_set(queryset=TemplateItem.objects.none())
        context_dict['formset'] = formset
        context_dict['form'] = form

    context_dict["extra"] = extra
    return render(request, 'create_template.html', context_dict)




def choose_curate_item(request,activity_name_slug):
    activity = Activity.objects.get(slug=activity_name_slug)
    print("MADE IT HERE YO")
    if request.method == 'POST':
        form = CurationItemChooseForm(request.POST , activity= activity)
        if form.is_valid():
            item = form.cleaned_data['item']
            return HttpResponseRedirect('/perspectivesX/curate/{}/{}/'.format(activity_name_slug,item.id))
        else:
            print form.errors
    else:
        form = CurationItemChooseForm(activity = activity)

    return render(request, 'choose_curation_item.html', {'form': form})




def curate_item(request, activity_name_slug, item  = None):

    context_dict = {}
    # retrieve the item to curate
    activity = Activity.objects.get(slug=activity_name_slug)
    #Check wether item is set, if not either let the user select one or assign one randomly
    if( item == None):
        curator_mode = activity.enable_curation
        SELECTED = 'Allow learners to choose a perspective to curate'
        RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
        ALL = 'Allow Learners to curate all perspectives'

        if curator_mode == SELECTED or curator_mode == ALL:
            return choose_curate_item(request,activity_name_slug)

        if curator_mode == RANDOM:
            item_list = list(LearnerSubmissionItem.objects.filter(
                learner_submission= LearnerPerspectiveSubmission.objects.filter(activity= activity)
            ))
            #the id is needed rather the the actual item object
            item = item_list[randint(0,len(item_list)-1)].id
    else:
        #parse the item id string into an integer
        item = int(item)

    if request.method == 'POST':
        form = ItemCuratorForm(request.POST, curator=User.objects.get(username = "marcolindley"), item = item)
        context_dict['form'] = form
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        #replace marcolindley with LTI user info
        form = ItemCuratorForm(curator=User.objects.get(username = "marcolindley"), item = item)
        context_dict['form']= form

    context_dict['item'] = LearnerSubmissionItem.objects.get(id = item).item
    return render(request, 'item_curator.html', context_dict)


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer


class TemplateItemViewSet(viewsets.ModelViewSet):
    queryset = TemplateItem.objects.all()
    serializer_class = TemplateItemSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class LearnerSubmissionViewSet(viewsets.ModelViewSet):
    queryset = LearnerPerspectiveSubmission.objects.all()
    serializer_class = LearnerPespectiveSubmissionSerializer


class LearnerSubmissionItemViewSet(viewsets.ModelViewSet):
    queryset = LearnerSubmissionItem.objects.all()
    serializer_class = LearnerSubmissionItemSerializer


class CuratedItemViewSet(viewsets.ModelViewSet):
    queryset = CuratedItem.objects.all()
    serializer_class = CuratedItemSerializer


class SubmissionScoreViewSet(viewsets.ModelViewSet):
    queryset = SubmissionScore.objects.all()
    serializer_class = SubmissionScoreSerializer

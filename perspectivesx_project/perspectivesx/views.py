from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from forms import ActivityForm, LearnerForm, LearnerSubmissionItemForm, TemplateCreatorForm, TemplateItemForm, \
    ItemCuratorForm, ItemChooseForm, deleteForm
from functools import partial, wraps
from django.forms import modelformset_factory, formset_factory
from models import Activity, Template, TemplateItem, LearnerSubmissionItem, LearnerPerspectiveSubmission, User
from rest_framework import viewsets, generics
from .serializers import *
from random import randint
from django.views.decorators.csrf import csrf_exempt
from django_auth_lti.decorators import lti_role_required
from django.views.decorators.clickjacking import xframe_options_exempt

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


@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student'], redirect_url='/perspectivesX/not_authorized/')
def LTIindex(request):
    print "resource_link_id", request.LTI.get('resource_link_id')
    print request.LTI
    print request.user
    if request.LTI.get('resource_link_id') is not None:
        msg = "Resource Link ID!" + request.LTI.get('resource_link_id')
    else:
        msg = "No Resource Link is set"
    return HttpResponse(msg)


def LTInot_authorized(request):
    return render(request, 'not_authorized.html', {'request': request})


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


def choose_perspective(request, activity_name_slug, user, all=False):
    activity = Activity.objects.get(slug=activity_name_slug)
    if (all):
        # the user must choose a perspective that he hasn't alread submited
        # retrive Submission for this activity from the user
        # !!!!!!!!!!!!!!!! UPDATE once LTI is set up !!!!!!!!!!!!
        already_submitted = LearnerPerspectiveSubmission.objects.filter(created_by=user).filter(activty=activity)
        # retrieve perspecitves from already_submited
        submitted_perspectives = TemplateItem.objects.filter(id__in=already_submitted.values('selected_perspective_id'))
        # retrive perspectives from template excluding the already submited ones
        queryset = TemplateItem.objects.filter(template=activity.template).exclude(id__in=submitted_perspectives)

    else:
        # !!!!! update to exclude items from curator once LTI is set up!!!!!!!!!!!
        queryset = TemplateItem.objects.filter(template=activity.template)

    if request.method == 'POST':
        form = ItemChooseForm(request.POST, queryset=queryset, item="perspective to submit")
        if form.is_valid():
            item = form.cleaned_data['item']
            return HttpResponseRedirect('/perspectivesX/submission/{}/{}/'.format(activity_name_slug, item.id))
        else:
            print form.errors
    else:
        form = ItemChooseForm(queryset=queryset, item="perspective to submit")

    return render(request, 'choose_item.html', {'form': form})


def student_submission(request, activity_name_slug, extra=0, perspective=None):
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
    # replace 'marcolindley' wiht LTI user info
    user = User.objects.get(username='marcolindley')
    # Check wether perspective is set, if not either let the user select one or assign one randomly
    if (perspective == None):
        perspective_mode = activity.perspective_selection
        SELECTED = 'Learner Selected'
        RANDOM = 'Randomly Assigned'
        ALL = 'Learner Completes All Perspectives'

        if perspective_mode == SELECTED:
            return choose_perspective(request, activity_name_slug, user)

        if perspective_mode == ALL:
            return choose_perspective(request, activity_name_slug, user, all=True)

        if perspective_mode == RANDOM:
            perspective_list = list(TemplateItem.objects.filter(
                template=activity.template
            ))
            # the id is needed rather the the actual item object
            perspective = perspective_list[randint(0, len(perspective_list) - 1)].id
    else:
        # parse the item id string into an integer
        perspective = int(perspective)

    context_dict = {'activity_name': activity.title}
    # retrieve the instance (it might not exists handle with a try except block)
    try:
        instance = LearnerPerspectiveSubmission.objects.filter(activity=activity).get \
            (created_by=user)
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
            context_dict['form'] = LearnerForm(activity=activity, user=user.username, perspective=perspective
                                               , instance=instance)
            input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm, extra=extra)
            # prepopulate the formset with pre_existing_answers
            formset = input_form_set(queryset=pre_existing_answers)
            context_dict['formset'] = formset

        else:  # When form is submited generate the form from the activity and template name
            form = LearnerForm(request.POST, perspective=perspective, activity=activity, user=user.username,
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
                    participation_score = min(1, float(i) / activity.minimum_contribution) * 100
                    # curation score = number of curated items on this activity by user/ activity.minimum_curation
                    # replace "marcoLindley" with LTI user info
                    curation_score = min(1, float(CuratedItem.objects.filter(
                        curator=user).filter(
                        item__in=LearnerSubmissionItem.objects.filter(
                            learner_submission=LearnerPerspectiveSubmission.objects.filter(
                                activity=activity))).count()) / activity.minimum_curation) * 100

                    total_score = (participation_score * activity.contribution_score / 100) + \
                                  (curation_score * activity.curation_score / 100)

                    score = SubmissionScore.objects.get_or_create(submission=submission)[0]
                    score.participation_grade = participation_score
                    score.curation_grade = curation_score
                    score.total_grade = total_score
                    score.save()

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
        context_dict['form'] = LearnerForm(perspective=perspective, activity=activity, user=user.username,
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

def delete_submission_item(request,item_id):
    """
    Delete a submission item and update the submission score
    :param request: django request
    :param item_id: the id of the item to be deleter
    """
    #retrieve item
    item = LearnerSubmissionItem.objects.get(id=item_id)
    if request.method == "POST":
        form = deleteForm(request.POST)
        if(form.is_valid()):
            choice = form.cleaned_data["choice"]
            if(choice == True):
                #retrieve score &activity associated with submission
                score = SubmissionScore.objects.get(submission=item.learner_submission)
                activity = Activity.objects.get(id = item.learner_submission.activity_id)
                #retrive number of items associated with this  -1 (counting as if the item was already deleted
                items = len(LearnerSubmissionItem.objects.filter(learner_submission = item.learner_submission))-1
                #update participation grade
                score.participation_grade = min(1,float(items/activity.minimum_contribution))*100
                #delete item
                item.delete()
        return index(request)
    else:
        form = deleteForm()
    return render(request, 'delete_item.html', {'form': form,'item':item})



def delete_curated_item(request,item_id):
    """
    Delete a curated item and update the submission score
    :param request:
    :param item_id:
    :return:
    """
    item = CuratedItem.objects.get(item_id=item_id)
    if request.method == "POST":
        form = deleteForm(request.POST)
        if (form.is_valid()):
            choice = form.cleaned_data["choice"]
            if (choice == True):
                # retrieve score &activity associated with submission
                score = SubmissionScore.objects.get(submission=item.item.learner_submission)
                activity = Activity.objects.get(id=item.item.learner_submission.activity_id)
                # retrive number of items associated with this  -1 (counting as if the item was already deleted
                items = len(CuratedItem.objects.filter(item__in =LearnerSubmissionItem.objects.filter(learner_submission= item.item.learner_submission_id))) - 1
                # update participation grade
                score.curation_grade = min(1, float(items / activity.minimum_curation)) * 100
                # delete item
                item.delete()
        return index(request)
    else:
        form = deleteForm()
    return render(request, 'delete_item.html', {'form': form, 'item': item.item})

def choose_curate_item(request, activity_name_slug, curator, all=False):
    activity = Activity.objects.get(slug=activity_name_slug)
    if (all):
        # retrive all LearnerSubmissionItems from activity
        # !!!!!!!!!!!!!!!! UPDATE TO EXCLUDE items from curator once LTI is set up !!!!!!!!!!!
        learner_submission_items = LearnerSubmissionItem.objects.filter(learner_submission__activity=activity)
            # retirve items already curated
        items_already_curated = CuratedItem.objects.filter(curator=curator).filter(item__in=learner_submission_items)
        # retrieve actual items from curated items
        items = LearnerSubmissionItem.objects.filter(id__in=items_already_curated.values('item_id'))
        # retrieve learner submission from actual items
        submissions = LearnerPerspectiveSubmission.objects.filter(id__in=items.values('learner_submission_id'))
        # retrieve perspectives from submissions
        perspectives_already_curated = TemplateItem.objects.filter(id__in=submissions.values('selected_perspective_id'))

        queryset = LearnerSubmissionItem.objects.filter(learner_submission=LearnerPerspectiveSubmission.objects.filter(
            activity=activity).exclude(selected_perspective__in=perspectives_already_curated))
    else:
        # !!!!! update to exclude items from curator once LTI is set up!!!!!!!!!!!
        queryset = LearnerSubmissionItem.objects.filter(
            learner_submission=LearnerPerspectiveSubmission.objects.filter(activity=activity))

    if request.method == 'POST':
        form = ItemChooseForm(request.POST, queryset=queryset, item="item to curate")
        if form.is_valid():
            item = form.cleaned_data['item']
            return HttpResponseRedirect('/perspectivesX/curate/{}/{}/'.format(activity_name_slug, item.id))
        else:
            print form.errors
    else:
        form = ItemChooseForm(queryset=queryset, item="item to curate")

    return render(request, 'choose_item.html', {'form': form})


def curate_item(request, activity_name_slug, item=None):
    context_dict = {}
    # retrieve the item to curate
    activity = Activity.objects.get(slug=activity_name_slug)
    # replace with LTI info
    curator = User.objects.get(username="marcolindley")
    # Check wether item is set, if not either let the user select one or assign one randomly
    if (item == None):
        curator_mode = activity.enable_curation
        SELECTED = 'Allow learners to choose a perspective to curate'
        RANDOM = 'Randomly assign a perspective that learners have not attempted for curation'
        ALL = 'Allow Learners to curate all perspectives'

        if curator_mode == SELECTED:
            return choose_curate_item(request, activity_name_slug, curator)

        if curator_mode == ALL:
            return choose_curate_item(request, activity_name_slug, curator, all=True)

        if curator_mode == RANDOM:
            item_list = list(LearnerSubmissionItem.objects.filter(
                learner_submission=LearnerPerspectiveSubmission.objects.filter(activity=activity)
            ))
            # the id is needed rather the the actual item object
            item = item_list[randint(0, len(item_list) - 1)].id
    else:
        # parse the item id string into an integer
        item = int(item)

    if request.method == 'POST':
        form = ItemCuratorForm(request.POST, curator=curator, item=item)
        context_dict['form'] = form
        if form.is_valid():
            # save the curated item
            form.save(commit=True)
            # update the grade of the SubmissionScore to reflect the new Curation score, update marcoLindley with lti user info
            score = SubmissionScore.objects.get(submission=
                                                LearnerPerspectiveSubmission.objects.filter(created_by=curator).
                                                get(activity=activity))

            # retrieve all items for this activity
            items = LearnerSubmissionItem.objects.filter(learner_submission=LearnerPerspectiveSubmission.objects.filter(
                activity=activity))
            # update curation score
            curation_score = min(1, (float(CuratedItem.objects.filter(curator=curator).filter(
                item__in=items).count()) / activity.minimum_curation)) * 100
            # update total score
            total_score = round((score.participation_grade * activity.contribution_score / 100) + \
                                (curation_score * activity.curation_score / 100))
            # update the score object
            score.curation_grade = curation_score
            score.total_grade = total_score
            # save
            score.save()

            return index(request)
        else:
            print form.errors
    else:
        # replace marcolindley with LTI user info
        form = ItemCuratorForm(curator=curator, item=item)
        context_dict['form'] = form

    context_dict['item'] = LearnerSubmissionItem.objects.get(id=item).item
    return render(request, 'item_curator.html', context_dict)


def display_perspective_items(request, activity, perspective):
    # retrieve all items for perspective of activity
    grid_activity = Activity.objects.get(id=activity);
    template_item = TemplateItem.objects.get(id=perspective)
    perspective_submissions = LearnerPerspectiveSubmission.objects.filter(activity=activity).filter(
        selected_perspective=perspective)
    perspective_items = LearnerSubmissionItem.objects.filter(learner_submission__in=perspective_submissions)

    return render(request, 'perspective_display.html',
                  {'items': perspective_items, 'perspective': template_item,
                   'activity': grid_activity})


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


class UserSubmissionItemList(generics.ListAPIView):
    """
    API List view used to retrieve all users submitted items for a particular perspective
    """
    serializer_class = LearnerSubmissionItemSerializer

    def get_queryset(self):
        perspective = self.kwargs['perspective']
        activity = self.kwargs['activity']
        # !!! replace this with proper user info !!!
        submissions = LearnerPerspectiveSubmission.objects.filter(activity = activity).filter(
            created_by=User.objects.get(username="marcolindley")).filter(selected_perspective=perspective)
        return LearnerSubmissionItem.objects.filter(learner_submission_id__in=submissions)


class UserCuratedItemList(generics.ListAPIView):
    """
    API List View used to retrieve all users Curated items for a particular perspective
    """
    serializer_class = LearnerSubmissionItemSerializer

    def get_queryset(self):
        perspective = self.kwargs['perspective']
        activity = self.kwargs['activity']
        submissions = LearnerPerspectiveSubmission.objects.filter(activity= activity).filter(selected_perspective=perspective)
        perspective_items = LearnerSubmissionItem.objects.filter(learner_submission__in=submissions)
        curated = CuratedItem.objects.filter(item__in=perspective_items).filter(
            curator=User.objects.get(username="marcolindley"))
        return LearnerSubmissionItem.objects.filter(id__in=curated.values('item'))


class PerspectiveList(generics.ListAPIView):
    """
    API List view used to retrieve all perspectives linked to an activity(Template Items)
    """
    serializer_class = TemplateItemSerializer

    def get_queryset(self):
        activity = Activity.objects.get(id = self.kwargs['activity'])
        return TemplateItem.objects.filter(template = activity.template)

class ActivityList(generics.ListAPIView):
    """
    API list view used to retrieve all Activities
    """
    serializer_class = ActivitySerializer

    def get_queryset(self):
        return Activity.objects.all()

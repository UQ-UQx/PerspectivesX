from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from perspectivesx.forms import ActivityForm, LearnerForm, LearnerSubmissionItemForm, TemplateCreatorForm, TemplateItemForm, \
    ItemCuratorForm, ItemChooseForm, deleteForm, AddLearnerSubmissionItemForm
from functools import partial, wraps
from django.forms import modelformset_factory, formset_factory
from perspectivesx.models import Activity, Template, TemplateItem, LearnerSubmissionItem, LearnerPerspectiveSubmission, User
from rest_framework import viewsets, generics
from .serializers import *
from random import randint
from django.views.decorators.csrf import csrf_exempt
from django_auth_lti.decorators import lti_role_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    activity_id = 1
    role = 'Administrator'
    display_view = "student_view"
    allowed_admin_roles = ['Administrator', 'Instructor']
    return render(request, 'index.html', {'role': role, 'display_view': display_view, 'allowed_admin_roles':allowed_admin_roles})

@xframe_options_exempt
def LTItest(request):
    """
    Defines view for the home page.
    At the moment just some text wiht link to add activity page
    :param request:
    :return:
    """
    return render(request, 'LTItest.html', {})

@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student', 'Administrator'], redirect_url='/perspectivesX/not_authorized/')
def LTIindex(request):
    activity_id = int(request.LTI.get('custom_activity_id'))
    role = request.LTI.get('roles')[0]

    resource_link_id = request.LTI.get('resource_link_id')
    request.session['perspectivesx_'+resource_link_id] =  request.LTI
    request.session['perspectivesx_'+resource_link_id]['activity_id'] =  activity_id
    display_view = "admin_view"
    allowed_admin_roles = ['Administrator', 'Instructor']

    if ((activity_id<=0) and (role in allowed_admin_roles)):
        return redirect('add_activity', resource_link_id=resource_link_id)
        #return add_activity(request,resource_link_id)
    else:
        return redirect('studentview', resource_link_id=resource_link_id)
        #return studentview(request,resource_link_id)

@xframe_options_exempt
def studentview(request,resource_link_id):

    LTI = request.session['perspectivesx_'+resource_link_id]
    activity_id = LTI.get('activity_id')
    #print("activity id after redirect", activity_id)
    #print(request.POST)
    role = LTI.get('roles')[0]
    #print("role", role)
    display_view = "student_view"
    allowed_admin_roles = ['Administrator', 'Instructor']

    #if student has made a perspectivesubmission display the grid_activity
    #else display the submission form
    username = "cuid:"+LTI.get('user_id')
    current_user = User.objects.get(username=username) #request.user
    user_id = current_user.id
    #username = current_user.username
    #print(user_id)
    learnersubmissions = LearnerPerspectiveSubmission.objects.filter(activity=activity_id,created_by=current_user.id)
    #print(learnersubmissions)
    if (len(learnersubmissions)>0):
        #print("Display grid")
        #load activity Terminology
        activity = Activity.objects.get(pk=activity_id)
        perspective_terminology = activity.perspective_terminology
        item_terminology = activity.item_terminology

        return render(request, 'index.html', {'role': role, 'display_view': display_view, 'allowed_admin_roles':allowed_admin_roles, 'resource_link_id':resource_link_id, 'username': username, 'user_id':user_id, 'activity_id': activity_id, 'perspective_terminology':perspective_terminology, 'item_terminology':item_terminology })
    else:
        #print("display submission form")
        return student_submission(request, resource_link_id, activity_id, extra=0, perspective=None)

@xframe_options_exempt
def LTInot_authorized(request):
    return render(request, 'not_authorized.html', {'request': request})

@xframe_options_exempt
def add_activity(request,resource_link_id):
    """
    defines view for add activity page
    Shows the add activity form
    :param request:
    :return:
    """
    #activity_id = 1
    LTI = request.session['perspectivesx_'+resource_link_id]
    activity_id = LTI.get('activity_id')
    #print("activity id after redirect", activity_id)
    #print(request.POST)
    role = LTI.get('roles')[0]
    #print("role", role)
    display_view = "admin_view"
    allowed_admin_roles = ['Administrator', 'Instructor']

    form = ActivityForm(request.POST or None, resource_link_id=resource_link_id)

    activity = None
    if (activity_id>0):
        activity = get_object_or_404(Activity, pk=activity_id)
        form = ActivityForm(request.POST or None, instance=activity, resource_link_id=resource_link_id)

    if request.POST and form.is_valid():
        activity = form.save(commit=True)
        request.session['perspectivesx_'+resource_link_id]['custom_activity_id']=str(activity.id)
        request.session['perspectivesx_'+resource_link_id]['activity_id']=activity.id
        #print("post save activity")
        #print(request.session['perspectivesx_'+resource_link_id])

        form = ActivityForm(request.POST or None, instance=activity, resource_link_id=resource_link_id)

        # Save was successful, so redirect to another page
        #redirect_url = reverse(article_save_success)
        #return redirect(redirect_url)
        #return index(request, resource_link_id)
    else:
        print(form.errors)

    return render(request, 'add_activity.html', {'form': form, 'role': role, 'resource_link_id': resource_link_id, 'display_view': display_view, 'allowed_admin_roles':allowed_admin_roles})

@xframe_options_exempt
def choose_perspective(request, resource_link_id, activity_id, user, all=False):
    activity = Activity.objects.get(id=activity_id)
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
            return HttpResponseRedirect('/perspectivesX/submission/{}/{}/{}/'.format(resource_link_id,activity_id, item.id))
        else:
            print(form.errors)
    else:
        form = ItemChooseForm(queryset=queryset, item="perspective to submit")

    return render(request, 'choose_item.html', {'form': form})

@xframe_options_exempt
def student_submission(request, resource_link_id, activity_id, extra=0, perspective=None):
    """
    View for student submission page
    Displays the submission form in function of the undertaken activity
    :param request: Django HTmlrequest
    :param activity_name_slug: slug name of the activity
    :return:
    """
    #print("student_submission")
    # retrieve information from parameters
    activity = Activity.objects.get(id=activity_id)
    #print(activity)
    template = Template.objects.get(name=activity.template)

    LTI = request.session['perspectivesx_'+resource_link_id]
    username = "cuid:"+LTI.get('user_id')
    user = User.objects.get(username=username) #request.user
    user_id = user.id
    # Check wether perspective is set, if not either let the user select one or assign one randomly
    if (perspective == None):
        perspective_mode = activity.perspective_selection
        '''
        SELECTED = 'Learner Selected'
        RANDOM = 'Randomly Assigned'
        ALL = 'Learner Completes All Perspectives'
        '''
        SELECTED = 'Allow learners to choose a perspective'
        RANDOM = 'Randomly assign a perspective for learner'
        ALL = 'Allow Learners to contribute to all perspectives'

        if perspective_mode == SELECTED:
            return choose_perspective(request, resource_link_id, activity_id, user)

        if perspective_mode == ALL:
            return choose_perspective(request, activity_id, user, all=True)

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
    context_dict['activity'] = activity
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
        #print('student submission posted')
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
            #form = LearnerForm(request.POST, perspective=perspective, activity=activity, user=user.username,
            #                   instance=instance)
            form = LearnerForm(request.POST, perspective=request.POST.get('selected_perspective'), activity=activity, user=user.username,
                               instance=instance)
            context_dict['form'] = form
            #print(request.POST)
            #print(perspective)
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

                    # # create the Submission score object attached to this submission
                    # # participation score = number of submited contribution/activity.minimum_contribution
                    # # max score is 100% hence limit i/activity.minimum_contribution to 1
                    # participation_score = min(1, float(i) / activity.minimum_contribution) * 100
                    # # curation score = number of curated items on this activity by user/ activity.minimum_curation
                    # # replace "marcoLindley" with LTI user info
                    # curation_score = min(1, float(CuratedItem.objects.filter(
                    #     curator=user).filter(
                    #     item__in=LearnerSubmissionItem.objects.filter(
                    #         learner_submission__in=LearnerPerspectiveSubmission.objects.filter(
                    #             activity=activity))).count()) / activity.minimum_curation) * 100
                    #
                    # total_score = (participation_score * activity.contribution_score / 100) + \
                    #               (curation_score * activity.curation_score / 100)

                    #score = SubmissionScore.objects.get(submission=submission)
                    # score.participation_grade = participation_score
                    # score.curation_grade = curation_score
                    #score.save()

                    #return index(request)
                    #print("about to run studentview")
                    return studentview(request,resource_link_id)

                else:
                    # Something went wrong when validating the formset remove the submission
                    submission.delete()
                    #print("random submission error")
                    #print(formset.errors)
                    input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm,
                                                          extra=extra)
                    formset = input_form_set(queryset=pre_existing_answers)
                    context_dict['formset'] = formset
            else:
                input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm,
                                                      extra=extra)

                formset = input_form_set(request.POST, queryset=pre_existing_answers)
                context_dict['formset'] = formset
                #print("random submission error2")
                #print(form.errors)

    else:

        context_dict['form'] = LearnerForm(perspective=perspective, activity=activity, user=user.username,
                                           instance=instance)

        input_form_set = modelformset_factory(LearnerSubmissionItem, form=LearnerSubmissionItemForm, extra=extra)
        formset = input_form_set(queryset=pre_existing_answers)
        context_dict['formset'] = formset
    context_dict['extra'] = extra

    #print(context_dict)
    return render(request, 'learner_submission.html', context_dict)

@xframe_options_exempt
def create_template(request, resource_link_id):
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
                    #return index(request)
                    redirect('studentview', resource_link_id=resource_link_id)
                else:
                    # Something went wrong when validating the formset remove the template
                    template.delete()
                    print(formset.errors)
            else:
                print(form.errors)
    else:
        form = TemplateCreatorForm()
        input_form_set = modelformset_factory(TemplateItem, form=TemplateItemForm, extra=extra)
        formset = input_form_set(queryset=TemplateItem.objects.none())
        context_dict['formset'] = formset
        context_dict['form'] = form

    context_dict["extra"] = extra
    return render(request, 'create_template.html', context_dict)


# def add_submission_item(request, activity_id, perspective_id, position, item):
#     """
#
#     :param request:
#     :param activity_id: id of the activity for the submission
#     :param perspective_id: id of the perspective for the submission
#     :param position: int representing position in list
#     :param item: actual submission linked to the item
#     :return:
#     """
#     submission = LearnerPerspectiveSubmission.objects.get(selected_perspective_id=perspective_id,
#                                                           activity_id=activity_id,
#                                                           created_by=User.objects.get(username="marcolindley"))
#     # manually add position and submission on form save
#     item = LearnerSubmissionItem.objects.create(item=item, position=int(position), learner_submission=submission)
#     item.save();
#
#     return index(request);


# def delete_submission_item(request, item_id):
#     """
#     Delete a submission item and update the submission score
#     :param request: django request
#     :param item_id: the id of the item to be deleter
#     """
#     # retrieve item
#     item = LearnerSubmissionItem.objects.get(id=item_id)
#     if request.method == "POST":
#         form = deleteForm(request.POST)
#         if (form.is_valid()):
#             choice = form.cleaned_data["choice"]
#             if (choice == "True"):
#                 # retrieve score &activity associated with submission
#                 score = SubmissionScore.objects.get(submission=item.learner_submission)
#                 activity = Activity.objects.get(id=item.learner_submission.activity_id)
#                 # retrive number of items associated with this  -1 (counting as if the item was already deleted
#                 items = len(LearnerSubmissionItem.objects.filter(learner_submission=item.learner_submission)) - 1
#                 # update participation grade
#                 score.participation_grade = min(1, float(items) / activity.minimum_contribution) * 100
#                 # update total grade
#                 score.total_grade = round((score.participation_grade * activity.contribution_score / 100) + \
#                                           (score.curation_grade * activity.curation_score / 100))
#                 score.save(force_update=True)
#                 # delete item
#                 item.delete()
#                 return delete_success(request, score.id)
#             else:
#                 return index(request)
#     else:
#         form = deleteForm()
#     return render(request, 'delete_item.html', {'form': form, 'item': item})


# def delete_curated_item(request, item_id):
#     """
#     Delete a curated item and update the submission score
#     :param request:
#     :param item_id:
#     :return:
#     """
#     item = CuratedItem.objects.get(item_id=item_id)
#     if request.method == "POST":
#         form = deleteForm(request.POST)
#         if (form.is_valid()):
#             choice = form.cleaned_data["choice"]
#             if (choice == "True"):
#                 # retrieve score &activity associated with submission
#                 score = SubmissionScore.objects.get(submission=item.item.learner_submission)
#                 activity = Activity.objects.get(id=item.item.learner_submission.activity_id)
#                 # retrive number of items associated with this  -1 (counting as if the item was already deleted
#                 items = len(CuratedItem.objects.filter(item__in=LearnerSubmissionItem.objects.filter(
#                     learner_submission=item.item.learner_submission_id))) - 1
#                 print(items)
#                 # update participation grade
#                 score.curation_grade = min(1, float(items) / activity.minimum_curation) * 100
#                 # update total grade
#                 score.total_grade = round((score.participation_grade * activity.contribution_score / 100) + \
#                                           (score.curation_grade * activity.curation_score / 100))
#
#                 score.save(force_update=True)
#                 # delete item
#                 item.delete()
#                 return delete_success(request, score.id)
#             else:
#                 return index(request)
#     else:
#         form = deleteForm()
#     return render(request, 'delete_item.html', {'form': form, 'item': item.item})


# def delete_success(request, updated_score):
#     score = SubmissionScore.objects.get(id=updated_score);
#     return render(request, "delete_success.html", {"score": score})

@xframe_options_exempt
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
            print(form.errors)
    else:
        form = ItemChooseForm(queryset=queryset, item="item to curate")

    return render(request, 'choose_item.html', {'form': form})

@xframe_options_exempt
def curate_item(request, activity_name_slug, item=None):
    context_dict = {}
    # retrieve the item to curate
    activity = Activity.objects.get(slug=activity_name_slug)
    # replace with LTI info
    curator = User.objects.get(username="cuid:a0d05d435d1a7bbf1e90f99400750bc5")
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
            curated = form.save(commit=True)
            # update the grade of the SubmissionScore to reflect the new Curation score, update marcoLindley with lti user info
            score = SubmissionScore.objects.get(submission=
                                                LearnerPerspectiveSubmission.objects.filter(created_by=curator).
                                                filter(activity=curated.item.learner_submission.activity_id).get(
                                                    selected_perspective=curated.item.learner_submission.selected_perspective))
            # save
            score.save()

            return index(request)
        else:
            print(form.errors)
    else:
        # replace marcolindley with LTI user info
        form = ItemCuratorForm(curator=curator, item=item)
        context_dict['form'] = form

    context_dict['item'] = LearnerSubmissionItem.objects.get(id=item).item
    return render(request, 'item_curator.html', context_dict)

@xframe_options_exempt
def display_perspective_items(request, activity, perspective, resource_link_id):

    LTI = request.session['perspectivesx_'+resource_link_id]
    username = "cuid:"+LTI.get('user_id')
    user = User.objects.get(username=username) #request.user
    user_id = user.id

    # retrieve all items for perspective of activity
    grid_activity = Activity.objects.get(id=activity);

    perspective_terminology = grid_activity.perspective_terminology
    item_terminology = grid_activity.item_terminology

    template_item = TemplateItem.objects.get(id=perspective)
    perspective_submissions = LearnerPerspectiveSubmission.objects.filter(activity=activity).filter(
        selected_perspective=perspective)
    perspective_items_list = LearnerSubmissionItem.objects.filter(learner_submission__in=perspective_submissions).order_by('-created_at')

    page = request.GET.get('page', 1)

    paginator = Paginator(perspective_items_list, 25)
    no_pages = paginator.num_pages
    try:
        perspective_items = paginator.page(page)
    except PageNotAnInteger:
        perspective_items = paginator.page(1)
    except EmptyPage:
        perspective_items = paginator.page(paginator.num_pages)

    return render(request, 'perspective_display.html',
                  {'resource_link_id':resource_link_id, 'items': perspective_items, 'perspective': template_item,
                   'activity': grid_activity, 'activity_id':activity, 'user_id':user_id, 'username':username,
                   'page':page, 'no_pages':no_pages,
                   'perspective_terminology': perspective_terminology, 'item_terminology': item_terminology})

'''
def index(request):
    user_list = User.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(user_list, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'core/user_list.html', { 'users': users })
'''

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
        username = self.kwargs['username']
        # !!! replace this with proper user info !!!
        submissions = LearnerPerspectiveSubmission.objects.filter(activity=activity).filter(
            created_by=User.objects.get(username=username)).filter(selected_perspective=perspective)

        return LearnerSubmissionItem.objects.filter(learner_submission_id__in=submissions).order_by('-created_at')


class UserCuratedItemList(generics.ListAPIView):
    """
    API List View used to retrieve all users Curated items for a particular perspective
    """
    serializer_class = CuratedItemSerializer

    def get_queryset(self):
        perspective = self.kwargs['perspective']
        activity = self.kwargs['activity']
        username = self.kwargs['username']
        submissions = LearnerPerspectiveSubmission.objects.filter(activity=activity).filter(
            selected_perspective=perspective)
        perspective_items = LearnerSubmissionItem.objects.filter(learner_submission__in=submissions)
        curated = CuratedItem.objects.filter(item__in=perspective_items).filter(
            curator=User.objects.get(username=username))
        return curated


class PerspectiveList(generics.ListAPIView):
    """
    API List view used to retrieve all perspectives linked to an activity(Template Items)
    """
    serializer_class = TemplateItemSerializer

    def get_queryset(self):
        activity = Activity.objects.get(id=self.kwargs['activity'])
        return TemplateItem.objects.filter(template=activity.template)



class GetSubmissionScore(generics.ListAPIView):
    serializer_class = SubmissionScoreSerializer

    def get_queryset(self):
        #return SubmissionScore.objects.filter(submission=self.kwargs['submission']);
        user_id = self.kwargs['userid']
        activity_id = self.kwargs['activity']
        user = User(id=user_id)
        activity = Activity.objects.get(id=activity_id)

        submission_count = LearnerSubmissionItem.objects.filter(learner_submission__created_by=user_id, learner_submission__activity=activity).count()
        #print("submission_count", submission_count);
        curated_count = CuratedItem.objects.filter(curator=user_id, item__learner_submission__activity=activity).count()

        #print("curated_count", curated_count);
        # calculate participation_grade
        participation_grade = min(1, float(submission_count / activity.minimum_contribution)) * 100
        # calculate contribution grade
        curation_grade = min(1, float(curated_count / activity.minimum_curation)) * 100
        # calculate total grade
        total_grade = ((participation_grade * activity.contribution_score) / 100) + (
            (curation_grade * activity.curation_score) / 100)

        #score,created = SubmissionScore.objects.get_or_create(user=self.learner_submission.created_by.id);

        submission_obj, created = SubmissionScore.objects.get_or_create(user=user);
        submission_obj.participation_grade=participation_grade
        submission_obj.curation_grade=curation_grade
        submission_obj.total_grade=total_grade

        submission_obj.save()

        return SubmissionScore.objects.filter(user=self.kwargs['userid']);

# class GetSubmissionFromCurated():
#     """
#     This API view retrieves the corresponding user submission from a curated item for that submission
#     IE
#         retrieve the submission that has the
#     """
#     serializer_class = LearnerSubmissionItemSerializer
#
#     def get_queryset(self):
#         return LearnerSubmissionItem.

from django.shortcuts import render
from django.http import HttpResponse
from forms import ActivityForm,LearnerForm
from models import Activity,Template,TemplateItem
def index(request):
    return render(request, 'index.html')

def add_activity(request):
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
    print(activity_name_slug)
    activity = Activity.objects.get(slug=activity_name_slug)
    template = Template.objects.get(name=activity.template)
    context_dict = {'activity_name':activity.title}
    if request.method == "POST":
        form = LearnerForm(request.POST, template_name = template.name )
        context_dict['form'] = form
        if form.is_valid():
            form.save(commit= True)
            return index(request)
        else:
            print(form.errors)
    else:
        context_dict['form'] = LearnerForm(template_name= template.name)

    return render(request, 'learner_submission.html', context_dict)


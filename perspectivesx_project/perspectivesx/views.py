from django.shortcuts import render
from django.http import HttpResponse
from forms import ActivityForm

def index(request):
    return render(request, 'index.html')

def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save(commit =True)
        else:
            print form.errors
    else:
        form = ActivityForm()

    return render(request, 'add_activity.html', {'form': form})

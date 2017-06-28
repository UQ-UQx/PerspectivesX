from django.contrib import admin
from models import Template, TemplateItem, Activity, LearnerSubmissionItem, LearnerPerspectiveSubmission

# Register your models here.
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class TemplateItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'template')
    search_fields = ('name', 'template')

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'template')
    search_fields = ('name', 'template')

class LearnerSubmissionAdmin(admin.ModelAdmin):
    list_display = ('item', 'position', 'template_item', 'activity')
    search_fields = ('item', 'position', 'template_item', 'activity')

class LearnerPerspectiveAdmin(admin.ModelAdmin):
    list_display = ('template_item', 'activity', 'perspective_selection')
    search_fields = ('template_item', 'activity', 'perspective_selection')

admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateItem, TemplateItemAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(LearnerSubmissionItem, LearnerSubmissionAdmin)
admin.site.register(LearnerPerspectiveSubmission, LearnerPerspectiveAdmin)

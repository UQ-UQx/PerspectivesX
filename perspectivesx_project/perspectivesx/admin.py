from django.contrib import admin
from models import Template, TemplateItem, Activity, LearnerSubmissionItem, LearnerPerspectiveSubmission, CuratedItem, SubmissionScore

# Register your models here.
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    search_fields = ('name',)

class TemplateItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'template')
    search_fields = ('name', 'template')

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'template')
    search_fields = ('title', 'template')
    prepopulated_fields = {'slug': ('title',)}

class LearnerSubmissionAdmin(admin.ModelAdmin):
    list_display = ('item', 'position', 'learner_submission')
    search_fields = ('item', 'position', 'learner_submission')

class LearnerPerspectiveAdmin(admin.ModelAdmin):
    list_display = ('selected_perspective','__unicode__' ,)
    search_fields = ('selected_perspective', 'activity',)

class CuratedItemAdmin(admin.ModelAdmin):
    search_fields = ('item','curator')

class SubmissionScoreAdmin(admin.ModelAdmin):
    search_fields = ('submission',)

admin.site.register(Template, TemplateAdmin)
admin.site.register(TemplateItem, TemplateItemAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(LearnerSubmissionItem, LearnerSubmissionAdmin)
admin.site.register(LearnerPerspectiveSubmission, LearnerPerspectiveAdmin)
admin.site.register(CuratedItem, CuratedItemAdmin)
admin.site.register(SubmissionScore , SubmissionScoreAdmin)

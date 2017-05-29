from django.contrib import admin

# Register your models here.
from .models import Question, Answer,UserAnswer, FreeTextAnswer,UserTextAnswer,Document,UserAudioAnswer

class AnswerTabularInline(admin.TabularInline):
	model = Answer



class QuestionAdmin(admin.ModelAdmin):
	inlines = [AnswerTabularInline]
	class Meta:
		model = Question

# class TestModelAdmin(admin.ModelAdmin):

# 	list_display = ('audio_file_player',)
# 	actions = ['custom_delete_selected']

# 	class Meta:
# 		model = TestModel

# 	def custom_delete_selected(self, request, queryset):
# 	    #custom delete code
# 	    n = queryset.count()
# 	    for i in queryset:
# 	        if i.audio_file:
# 	            if os.path.exists(i.audio_file.path):
# 	                os.remove(i.audio_file.path)
# 	        i.delete()
# 	    self.message_user(request, ("Successfully deleted %d audio files.") % n)
# 	custom_delete_selected.short_description = "Delete selected items"

# 	def get_actions(self, request):
# 	    actions = super(AudioFileAdmin, self).get_actions(request)
# 	    del actions['delete_selected']
# 	    return actions

admin.site.register(UserTextAnswer)
admin.site.register(FreeTextAnswer)
admin.site.register(UserAudioAnswer)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserAnswer)
admin.site.register(Document)

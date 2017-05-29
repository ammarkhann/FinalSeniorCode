from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver	
from django.db.models import Q
import os.path

# Create your models here.

Question_Types_Choices = (
    ('multiple_choice', ('multiple_choice')),
    ('audio_input', ('audio_input')),
    ('text_input', ('text_input'))
)

class QuestionManager(models.Manager):
	def get_unanswered(self, user):
		q1 = Q(useranswer__user = user)
		q2 = Q(usertextanswer__user = user)
		q3 = Q(useraudioanswer__user = user)
		qs = self.exclude(q1 | q2 | q3)
		return qs

	# def get_usertext_unanswered(self,user):
	# 	q1 = Q(usertextanswer__user = user)
	# 	qs = self.exclude(q1)
	# 	return qs

class Question(models.Model):
	text = models.TextField()
	active = models.BooleanField(default=True)
	question_type = models.CharField(max_length = 250, choices =Question_Types_Choices)
	timestamp = models.DateTimeField(auto_now_add=True , auto_now=False)
	
	objects = QuestionManager()


	def __unicode__(self):
		return self.text[:10]

class Answer(models.Model):
	answers = models.ForeignKey(Question)
	text = models.TextField(blank=True,null=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True , auto_now=False)

	def __unicode__(self):
		return self.text[:10]

class FreeTextAnswer(models.Model):
	answers = models.ForeignKey(Question)
	text = models.TextField(blank=True, null=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True , auto_now=False)

	def __unicode__(self):
		return self.text[:10]


class UserAnswer(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)  
	my_answer = models.ForeignKey(Answer)
	my_points = models.IntegerField(default=-1)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)


	def __unicode__(self):
		return self.my_answer.text[:10]



class UserTextAnswer(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)  
	my_answer = models.ForeignKey(FreeTextAnswer)
	translated_answer = models.TextField(null=True, blank=True)
	my_points = models.IntegerField(default=-1)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.my_answer.text[:10]


def upload_to(instance, filename):

	return os.path.join('/%s/' % instance.user.username, filename)

class UserAudioAnswer(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	audio_file = models.FileField(upload_to=upload_to)
	turkish_speech_to_text = models.TextField(null=True,blank=True)
	translated_english_answer = models.TextField(null=True, blank=True)

	my_points = models.IntegerField(default=-1)
	
	def __unicode__(self):
		return self.question.text




class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

def score_calculation(instance):

	obj = Question.objects.get(id=instance.question.id)
	for idx, ans in enumerate(obj.answer_set.all()):

		if ans == instance.my_answer and idx == 0:
			points = 100
			return points
		elif ans == instance.my_answer and idx == 1:
			points = 75
			return points

		elif ans == instance.my_answer and idx == 2:
			points = 50
			return points

		elif ans == instance.my_answer and idx == 3:
			points = 25
			return points



			
@receiver(pre_save, sender=UserAnswer)
def update_user_answer_score(sender,instance,*args,**kwargs):	
	my_points = score_calculation(instance)
	instance.my_points = my_points
	












# -*- coding: utf-8 -*-
import io
from django.conf import settings
from django.http import Http404,HttpResponseRedirect
from httplib2 import Http
from django.shortcuts import render, get_object_or_404,redirect
from googleapiclient.discovery import build
from googleapiclient import discovery
from django.core.urlresolvers  import reverse
from oauth2client.service_account import ServiceAccountCredentials
import speech_recognition as sr
import io
import os
from os.path import join
import time
from google.cloud import speech
from django.core.files.base import ContentFile
from django.core.files import File
import datetime

# Create your views here.

from .forms import UserResponseForm,UserTextFreeForm,DocumentForm
from .models import Question, Answer, UserAnswer,UserTextAnswer, FreeTextAnswer,Document,UserAudioAnswer

def single(request,id):
	if request.user.is_authenticated():

		service = build('translate', 'v2',
            developerKey='AIzaSyBeClQpB9mVa_kp0YjgBPn3U35Z5QnL-wI')
		
		#FOR LOCAL USE
		# path = "/Users/ammarkhan/Downloads/sentiment-analysis-921a452139e2.json"
		#FOR HEROKU USE

		path = os.path.join(settings.BASE_DIR, "sentiment-analysis-921a452139e2.json")
		#FOR ONLINE
		# path = "/home/ammarkhan123/webapps/depressionassessment/SentimentAnalysis-bdc3f8ec8bc8.json"
		scopes = ['https://www.googleapis.com/auth/cloud-platform']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scopes)

		http_auth = credentials.authorize(Http())
		service_sentiment = discovery.build('language', 'v1', credentials=credentials)


		queryset = Question.objects.all().order_by('-timestamp')
		instance = get_object_or_404(Question, id=id)

		
		try:
			user_answer = UserAnswer.objects.get(user=request.user, question=instance)
			updated_q = True
		except UserAnswer.DoesNotExist:
			user_answer = UserAnswer()
			updated_q = False
		except UserAnswer.MultipleObjectsReturned:
			user_answer = UserAnswer.objects.filter(user=request.user, question=instance)[0]
			updated_q = True
		except:
			user_answer = UserAnswer()
			updated_q = False

		try:
			user_audio_answer = UserAudioAnswer.objects.get(user=request.user,question=instance)
			updated_user_audio_answer = True
		except UserAudioAnswer.DoesNotExist:
			updated_user_audio_answer = False
			user_audio_answer = UserAudioAnswer()
		except UserAudioAnswer.MultipleObjectsReturned:
			user_audio_answer = UserAudioAnswer.objects.filter(user=request.user, question=instance)[0]
			updated_user_audio_answer = True
		except:
			user_audio_answer = UserAudioAnswer()
			updated_user_audio_answer = False




		try:
			user_text_answer = UserTextAnswer.objects.get(user=request.user, question=instance)
			updated_user_text_answer = True
			initial_dict = {
			"my_answer": user_text_answer.my_answer.text
			}
		except UserTextAnswer.DoesNotExist:
			updated_user_text_answer = False
			user_text_answer = UserTextAnswer()
			initial_dict = {
			
			}
		except UserTextAnswer.MultipleObjectsReturned:
			user_text_answer = UserTextAnswer.objects.filter(user=request.user, question=instance)[0]
			updated_user_text_answer = True
			initial_dict = {
			"my_answer": user_text_answer.my_answer.text
			}
		except:
			user_text_answer = UserTextAnswer()
			updated_user_text_answer = False
			initial_dict = {
			
			}


		
		try:
			free_text_answer = FreeTextAnswer.objects.get(answers_id=instance.id)
		except FreeTextAnswer.DoesNotExist:
			free_text_answer = FreeTextAnswer()
		except FreeTextAnswer.MultipleObjectsReturned:
			free_text_answer = FreeTextAnswer.objects.filter(answers_id=instance.id)[0]
		except:
			free_text_answer = FreeTextAnswer()

		


		form2 = UserTextFreeForm(request.POST or None, initial = initial_dict)	
		form = UserResponseForm(request.POST or None)

		audio_file_path = None
		


		r = sr.Recognizer()
		if instance.question_type == 'audio_input':

			print request.GET
			if '_start' in request.GET:
				print("Start Recording")
				
				audio_file_path = start_recording(r,request)
				question_instance = Question.objects.get(id=instance.id)
				user_audio_answer.user = request.user
				user_audio_answer.question = question_instance
		

				turkish_speech_to_text = r.recognize_google(user_received_audio, language = "tr-TR")
				user_audio_answer.turkish_speech_to_text = turkish_speech_to_text

				abc = service.translations().list(
						 	 source='tr',
						target='en',
						q=[turkish_speech_to_text]
				).execute()

				turkish_translated_text = abc['translations'][0]['translatedText']

				user_audio_answer.translated_english_answer = turkish_translated_text


				service_request = service_sentiment.documents().analyzeSentiment(
					body={
					'document': {
					'type': 'PLAIN_TEXT',
					'content': turkish_translated_text,
					}
				}
				)

				response = service_request.execute()

				score = response['documentSentiment']['score']
				

				real_score = calculate_user_score(score)
				user_audio_answer.my_points = real_score
				user_audio_answer.save()
			elif '_submit' in request.GET:
				
				if user_audio_answer.my_points is not -1:
					next_q = Question.objects.get_unanswered(request.user).order_by("?")
					if next_q.count() > 0:
						next_q_instance = next_q.first()
						return redirect("question_single",id=next_q_instance.id)
					else:
						return redirect("home")


			if request.GET.get('StartRecording') == 'StartRecording':
				r = sr.Recognizer()
				with sr.Microphone() as source:
					print("Say something!")
					audio = r.listen(source)

				speech_to_text = r.recognize_google(user_received_audio, language = "tr-TR")
			
				question_instance = Question.objects.get(id=instance.id)
				free_text_answer.answers = question_instance
				free_text_answer.text = speech_to_text
				free_text_answer.save()





	
		if form2.is_valid():
			
			
			question_id = form2.cleaned_data.get('question_id')
			user_text_input = form2.cleaned_data.get('my_answer')

			question_instance = Question.objects.get(id=question_id)
			
			
			free_text_answer.answers = question_instance
			free_text_answer.text = user_text_input
			free_text_answer.save()

			

			abc = service.translations().list(
	 					 	 source='tr',
  						target='en',
  						q=[user_text_input]
					).execute()

			print abc
			turkish_translated_text = abc['translations'][0]['translatedText']

			


			service_request = service_sentiment.documents().analyzeSentiment(
 				 body={
   			 			'document': {
    			  		'type': 'PLAIN_TEXT',
    				  'content': turkish_translated_text,
   					 }
 		 				}
					 )
			response = service_request.execute()

			score = response['documentSentiment']['score']
			magnitude = response['documentSentiment']['magnitude']

			real_score = calculate_user_score(score)

			print "The score is %s and the magnitude of this sentence is %s" %(score,magnitude)

			user_text_answer.user = request.user
			user_text_answer.question = question_instance
			user_text_answer.my_answer = free_text_answer
			user_text_answer.translated_answer = turkish_translated_text
			user_text_answer.my_points = real_score
			user_text_answer.save()
			
			next_q = Question.objects.get_unanswered(request.user).order_by("?")
			print "The qs from form 2 is %s" %(next_q)
			if next_q.count() > 0:
				next_q_instance = next_q.first()
				return redirect("question_single",id=next_q_instance.id)
			else:
				return redirect("home")

		if form.is_valid():

			question_id = form.cleaned_data.get('question_id') #form.cleaned_data['question_id']
			answer_id = form.cleaned_data.get('answer_id')
			question_instance = Question.objects.get(id=question_id)
			answer_instance = Answer.objects.get(id=answer_id)
		

			user_answer.user = request.user
			user_answer.question = question_instance
			user_answer.my_answer = answer_instance
			user_answer.save()


			next_q = Question.objects.get_unanswered(request.user).order_by("?")
			print "The qs from form 1 is %s" %(next_q)
			if next_q.count() > 0:

				next_q_instance = next_q.first()

				return redirect("question_single",id=next_q_instance.id)
			else:
				
				return redirect("home")
		
		context = {
			"form": form,
			"form2": form2,
			"instance": instance,
			"user_answer": user_answer,
			"user_text_answer": user_text_answer,
			"free_text_answer": free_text_answer,
			"user_audio": user_received_audio,
			"user_audio_answer": user_audio_answer,
			"audio_file_path": audio_file_path,
			
		}
		return render(request, "questions/single.html", context)
	else:
		raise Http404



def calculate_user_score(score):
	score_range_constant = 0.6
	total_score_range = 1.4

	temp_score = score+score_range_constant
	actual_score = temp_score/total_score_range
	score_percentage = actual_score*100
	return score_percentage


def home(request):
	if request.user.is_authenticated():
		form = UserResponseForm(request.POST or None)
		if form.is_valid():
			question_id = form.cleaned_data.get('question_id') #form.cleaned_data['question_id']
			answer_id = form.cleaned_data.get('answer_id')
			question_instance = Question.objects.get(id=question_id)
			answer_instance = Answer.objects.get(id=answer_id)
			print answer_instance.text, question_instance.text

		queryset = Question.objects.all().order_by('-timestamp')
		instance = queryset[1]
		context = {
			"form": form,
			"instance": instance,
			#"queryset": queryset
		}
		return render(request, "questions/home.html", context)
	else:
		raise Http404




user_received_audio = None


def start_recording(r,request):

	print("Reached start recording metho. About to start recording")


	with sr.Microphone() as source:
		print("Say something!")
		audio = r.record(source,duration=10)

	global user_received_audio
	user_received_audio = audio
	random_file_name = request.user.username + "-" + datetime.datetime.now().strftime('%d:%m:%Y')
	full_path = save_user_audio_file(request,random_file_name)
	return full_path

def save_user_audio_file(request,file_name):
	
	path = settings.MEDIA_ROOT+"/"+request.user.username
	full_path = os.path.join(path,file_name)
	with open(full_path+".flac","wb") as f:
		f.write(user_received_audio.get_flac_data())
	full_path = full_path+".flac"
	print("audio file saved")
	return full_path









from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages
from google.cloud import speech

from newsletter.forms import ContactForm, SignUpForm
from newsletter.models import SignUp
from django.shortcuts import render, get_object_or_404,redirect
from questions.models import Question,UserAnswer,UserTextAnswer, UserAudioAnswer
import speech_recognition as sr
import io
import os
import time
from questions.models import Question

		

# Create your views here.
def home(request):
	
	if request.user.is_authenticated():

		queryset = Question.objects.all().order_by('-timestamp')

		new_user = False
	
		context = {
			"new_user": new_user,
			"question": queryset[0],
		}


		
		return render(request, "dashboard/home.html", context)

	context = {
		
	}


	return render(request, "home.html", context)


def test(request):

	uri = 'gs://12depressionassessment34/test123.flac'
	
	path = "/Users/ammarkhan/Downloads/sentiment-analysis-921a452139e2.json"
	# r = sr.Recognizer()
	# r.pause_threshold=5
	# r.phrase_threshold = 0.3
	# with sr.Microphone() as source:
	# 	print("Say something!")
	# 	print(r.pause_threshold)
	# 	audio = r.listen(source)

	file_name = "test123"
	path = settings.MEDIA_ROOT+"/"+request.user.username
	full_path = os.path.join(path, file_name)
	print("The file name is %s and the path is %s where the full path is %s" %(file_name,path,full_path)) 
	# if not os.path.exists(path):
	# 	os.makedirs(path)

	# with open(full_path+".flac","wb") as f:
	# 	f.write(audio.get_flac_data())

	# print("audio file saved")
	alter = transcribe_gcs(uri)




	# AUDIO_FILE_TR = os.path.join(settings.MEDIA_ROOT+"/"+request.user.username, "test123.flac")
	# print AUDIO_FILE_TR
	# r = sr.Recognizer()
	# with sr.AudioFile(filepath) as source:
	# 	print("about to read the file")
	# 	print(source)
	# 	audio_tr = r.record(source)

	# print("reading done")
	# print(audio_tr)

	return render(request,"dashboard/long_audio.html", context={"alter": alter,})


def result(request):
	queryset = Question.objects.get_unanswered(request.user).order_by('-timestamp')	

	if queryset.count() == 0:
		multiple_choice_score = 0
		text_score = 0
		audio_score = 0

		user_answer = UserAnswer.objects.filter(user=request.user)
		user_text_answer = UserTextAnswer.objects.filter(user=request.user)
		user_audio_answer = UserAudioAnswer.objects.filter(user=request.user)
		print user_text_answer

		for obj in user_answer:
			multiple_choice_score += obj.my_points

		for obj in user_text_answer:
			text_score += obj.my_points

		for obj in user_audio_answer:
			audio_score += obj.my_points

		temp_user_score = (multiple_choice_score + text_score + audio_score)/ (user_answer.count() + user_text_answer.count()+ user_audio_answer.count())
		print temp_user_score

		
	else:
		print messages.error(request, 'Please answer all the questions first.')
		return redirect("home")

	context = {

	"temp_user_score": temp_user_score,
	}



	return render(request,"dashboard/result.html", context)





def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    print("Executing gcs method")
    from google.cloud import speech
    speech_client = speech.Client()

    audio_sample = speech_client.sample(
        content=None,
        source_uri=gcs_uri,
        encoding='FLAC',
        sample_rate_hertz=16000)

    operation = audio_sample.long_running_recognize('tr-TR')
    print("checkpoint2")
    retry_count = 100
    while retry_count > 0 and not operation.complete:
        retry_count -= 1
        time.sleep(2)
        operation.poll()


    print("checkpoint3")

    if not operation.complete:
        print('Operation not complete and retry limit reached.')
        return

    print("checkpoint 4")

    alternatives = operation.results

    return alternatives

    # for alternative in alternatives:
    #     print('Transcript: {}'.format(alternative.transcript))
    #     print('Confidence: {}'.format(alternative.confidence))
    # [END send_request_gcs]


def user_agreement(request):
	return render(request,"dashboard/user-agreement.html", context={})





















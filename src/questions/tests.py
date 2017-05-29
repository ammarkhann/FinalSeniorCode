from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
from .models import Question,Answer



class QuestionTestCase(TestCase):

	def setUp(self):

		Question.objects.create(text="This is a test question?", question_type="multiple_choice")

        

	def test_question_is_not_null(self):
		
		question = Question.objects.get(text="This is a test question?")

		self.assertTrue(question.text)

	def test_question_choice_exists(self):

		question = Question.objects.get(text="This is a test question?")
		self.assertTrue(question.question_type )



class AnswerTestCase(TestCase):

	def setUp(self):
		q = Question.objects.create(text="This is a test question?", question_type="multiple_choice")

		Answer.objects.create(answers=q, text = "GOOD")


	def test_answer_is_not_null(self):

		answer = Answer.objects.get(answers=1)

		self.assertTrue(answer.answers)
		self.assertTrue(answer.text)








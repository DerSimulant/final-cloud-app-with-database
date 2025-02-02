import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings

import uuid



# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# <HINT> Create a Question Model with:
    # Used to persist question content for a course
    # Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
    # Has a grade point for each question
    # Has question content
    # Other fields and methods you would like to design
class Question(models.Model):
       # One-To-Many relationship with Course model
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    # Question text content
    text = models.TextField()

    # Grade point for the question
    grade_point = models.PositiveSmallIntegerField()

    # Other fields and methods you would like to include
    # ...
    def __str__(self):
        return self.text
    #def is_get_score(self, selected_choice_ids):
       # """Evaluate if the question was answered correctly by comparing the selected choice ids with correct choices in the question."""
      #  correct_choice_ids = [choice.id for choice in self.choices.all() if choice.is_correct]
        #return set(selected_choice_ids) == set(correct_choice_ids)
    # Foreign key to lesson
    # question text
    # question grade/mark

    # <HINT> A sample model method to calculate if learner get the score of the question
    #def is_get_score(self, selected_ids):
       # all_answers = self.choice_set.filter(is_correct=True).count()
       # selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
       # if all_answers == selected_correct:
        #    return True
       # else:
       #     return False

     #def calculate_score(self):
       # total_score = 0
       # for choice in self.choices.all():
        #    question = choice.question
        #    if choice.is_correct:
         #       total_score += question.grade_point
        #self.score = total_score
        #self.save()


#  <HINT> Create a Choice Model with:
    # Used to persist choice content for a question
    # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    # Choice content
    # Indicate if this choice of the question is a correct one or not
    # Other fields and methods you would like to design
class Choice(models.Model):
     # One-To-Many relationship with Question model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # Choice text content
    text = models.TextField()

    # Indicate if this choice is a correct one or not
    is_correct = models.BooleanField(default=False)

    # Other fields and methods you would like to include
    # ...
    def __str__(self):
        return self.text
# <HINT> The submission model
# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
#class Submission(models.Model):
    #enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    #choices = models.ManyToManyField(Choice)
    #Other fields and methods you would like to design
    
class Submission(models.Model):
    # One-to-Many relationship with Enrollment
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)

    # Many-to-Many relationship with choices
    choices = models.ManyToManyField(Choice)
    # new field for correct choices
    correct_choices = models.IntegerField(default=1)

    total_score = models.IntegerField(default=0)
    selected_choices = models.BooleanField(default=False)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)
    total_attempted = models.IntegerField(default=0)
    total_not_attempted = models.IntegerField(default=0)
    percentage_correct = models.IntegerField(default=0)

    
    def calculate_score(question_ids):
        total_score = 0
        for question_id in question_ids:
            question = get_object_or_404(Question, pk=question_id)
            choices = Choice.objects.filter(question=question)
            score = 0
            total_correct_choices = 0
            total_submitted_choices = 0
            for choice in choices:
                if choice.is_correct:
                    total_correct_choices += 1
                total_submitted_choices += 1

            if total_submitted_choices != 0:
                if total_correct_choices == total_submitted_choices:
                    score = question.grade_point
                else:
                    score = (total_correct_choices / total_submitted_choices) * question.grade_point
            else:
                score = 0
            total_score += score
        return total_score
      
        

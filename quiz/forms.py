from django import forms
from django.contrib.auth.models import User
from . import models

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))



class CourseForm(forms.ModelForm):
    class Meta:
        model=models.Course
        fields=['course_name','question_number','total_marks']

class QuestionForm(forms.ModelForm):
    courseID = forms.ModelChoiceField(queryset=models.Course.objects.all(), empty_label="Category Name", to_field_name="id")

    class Meta:
        model = models.Question
        fields = ['marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer', 'hint']  # Include 'hint' here
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'hint': forms.Textarea(attrs={'rows': 2, 'cols': 50, 'placeholder': 'Provide a hint (optional)'})  # Optional widget
        }

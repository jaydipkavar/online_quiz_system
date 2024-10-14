from django.shortcuts import render,redirect,reverse,get_object_or_404
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    # Get the currently logged-in student
    student = request.user  # Assuming the user is a student instance

    # Fetch results for this student
    results = QMODEL.Result.objects.filter(student__id=student.pk)

    # Optionally, you can get all courses as well if needed for display
    courses = QMODEL.Course.objects.all()

    return render(request, 'student/student_marks.html', {
        'results': results,
        'courses': courses,
    })
  

def quiz_view(request, course_id):
    course = get_object_or_404(QMODEL.Course, id=course_id)
    questions = list(course.question_set.all())
    current_question_index = int(request.POST.get('current_question_index', 0))
    
    if 'score' not in request.session:
        request.session['score'] = 0

    feedback_message = ""

    if request.method == 'POST':
        selected_answer = request.POST.get('answer')
        correct_answer = questions[current_question_index].answer
        marks = questions[current_question_index].marks 

        if selected_answer == correct_answer:
            request.session['score'] += marks  
            feedback_message = "<span class='text-success'>Correct! You earned {} marks.</span>".format(marks)
        else:
            feedback_message = "<span class='text-danger'>Wrong! The correct answer is: {}. You earned 0 marks.</span>".format(correct_answer)

        current_question_index += 1 

    if current_question_index >= len(questions):
        score = request.session['score']  
        del request.session['score']  
        return redirect('quiz_complete_view', course_id=course.id, score=score)

    current_question = questions[current_question_index]
    
    context = {
        'course': course,
        'current_question': current_question,
        'current_question_index': current_question_index,
        'current_question_hint': current_question.hint,
        'feedback_message': feedback_message,
    }

    print("Context being sent to the template:", context)

    return render(request, 'quiz/question.html', context)


def quiz_complete_view(request, course_id, score):
    course = get_object_or_404(QMODEL.Course, id=course_id)
    
    # Calculate total marks
    total_marks = sum(question.marks for question in course.question_set.all())
    
    # Save the result
    if request.user.is_authenticated:  # Ensure the user is authenticated
        student = request.user.student  # Assuming you have a one-to-one relation with Student
        QMODEL.Result.objects.create(student=student, exam=course, marks=score)

    context = {
        'course': course,
        'attempted_marks': score,
        'total_marks': total_marks,
    }
    return render(request, 'quiz/complete.html', context)
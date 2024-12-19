from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,HttpResponseRedirect
from OTS.models import *
import random

def welcome(request):
    template=loader.get_template('welcome.html')
    return HttpResponse(template.render())
def candidateRegistrationForm(request):
    res=render(request,'registration_form.html')
    return res
def candidateRegistration(request):
    if request.method=='POST':
        username=request.POST['username']
        # check if the user already exists
        if len(Candidate.objects.filter(username=username)):
            userStatus=1
        else:
            
            candiate=Candidate()
            candiate.username=username
            candiate.password=request.POST['password']
            candiate.name=request.POST['name']
            candiate.save()
            userStatus=2
    else:
        userStatus=3 #Request method is not POST
    context = {
        'user-status':userStatus
    }
    res=render(request,'registration.html',context)
    return res

def loginView(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        candidate=Candidate.objects.filter(username=username,password=password)
        if len(candidate)==0:
            loginError='Invalid Username or Password'
            res=render(request,'login.html',{'loginError':loginError})
        else:
            #login Success
            request.session['username']=candidate[0].username
            request.session['name']=candidate[0].name
            res=HttpResponseRedirect("home")
    else:
        res=render(request,'login.html')
    return res
def candidateHome(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    else:
        res=render(request,'home.html')
    return res
def testPaper(request):
    if 'name' not in request.session.keys():
        res=HttpResponseRedirect("login")
    #fetch question from database table
    n=int(request.GET['n'])
    question_pool=list(Question.objects.all())
    random.shuffle(question_pool)
    question_list=question_pool[:n]
    context={'questions':question_list}
    res=render(request,'test_paper.html',context)
    return res
def calculateTestResult(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect("login")
    total_attempt=0
    total_right=0
    total_wrong=0
    qid_list=[]
    for k  in request.POST:
        if k.startswith('qno'):
            qid_list.append(int(request.POST[k]))
    for n in qid_list:
        question=Question.objects.get(qid=n)
        try:
            if question.ans==request.POST['q'+str(n)]:
                total_right+=1
            else:
                total_wrong+=1
        except:
            pass
    points = (total_right - total_wrong) / len(qid_list) * 10 if qid_list else 0
    #store result in result table
    result=Result()
    result.username=Candidate.objects.get(username=request.session['username'])
    result.attempt=total_attempt
    result.right=total_right
    result.wrong=total_wrong
    result.points=points
    result.save()
    #update candidate table
    candidate=Candidate.objects.get(username=request.session['username'])
    candidate.test_attempted+=1
    candidate.points=(candidate.points*(candidate.test_attempted-1)+points)/candidate.test_attempted
    candidate.save()
    return HttpResponseRedirect('result') 
from django.shortcuts import render, redirect
from .models import Candidate, Result  # Adjust the import based on your project structure

def testResultHistory(request):
    if 'name' not in request.session.keys():
        return HttpResponseRedirect("login")
    
    try:
        candidate = Candidate.objects.get(username=request.session['username'])
    except Candidate.DoesNotExist:
        return HttpResponseRedirect("login")  # Redirect if candidate is not found
    
    results = Result.objects.filter(username=candidate)
    
    context = {'candidate': candidate, 'results': results}
    return render(request, 'candidate_history.html', context)
def showTestResult(request):
     if 'name' not in request.session.keys():
        return HttpResponseRedirect("login")
        
     #fetch latest result from Result Table
     result=Result.objects.filter(resultid=Result.objects.latest('resultid').resultid,username_id=request.session['username'])
     context={'result':result}
     return render(request,'show_result.html',context)
def logoutView(request):
    if 'name'  in request.session.keys():
        del request.session['username']
        del request.session['name']
    return HttpResponseRedirect("login")
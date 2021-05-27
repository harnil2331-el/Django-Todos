from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        c = Todo.objects.filter(user=request.user, datecompleted__isnull=False).count()
        todos =Todo.objects.filter(user=request.user, datecompleted__isnull=True,delete =False).count()
        u = Todo.objects.filter(user =request.user)
        return render(request, 'todo/home.html',{'c':c,'todos':todos,'u':u})
    else:
        return render(request, 'todo/home.html')
def signupuser(request):
    if request.method == 'GET':
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodoss')
            except IntegrityError:
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':'username has been already taken'})

        else:
            return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':'password didnt match'})
            #tell the user password didnt match

def loginuser(request):
    if request.method == 'GET':
        return render(request,'todo/login.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/login.html',{'form':AuthenticationForm(),'error':"incorrect credential"})
        else:
            login(request, user)
            return redirect('home')



@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


# --------------------Todos----------------------------------------
@login_required
def createtodos(request):
    if request.method == 'GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            ntodo = form.save(commit=False)
            ntodo.user = request.user
            ntodo.save()
            return redirect('currenttodoss')
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':TodoForm(),'error':'bad data passed in'})
#delete=false because when someone delete todos it will change delete value to true so,
# they cant see deleted todos but it is in database
@login_required
def currenttodoss(request):
    todos =Todo.objects.filter(user=request.user, datecompleted__isnull=True, delete=False)
    return render(request, 'todo/currenttodos.html',{'todos':todos})

@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html',{'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodoss')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'error':'bad data passed in'})

@login_required
def complete(request,todo_pk):
        todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)
        if request.method == 'POST':
            todo.datecompleted = timezone.now()
            todo.save()
            return redirect('currenttodoss')

#this deletetodo is not delete todos in database it will only show user that, it is deleted .
@login_required
def deletetodo(request,todo_pk):
        todo = get_object_or_404(Todo,pk=todo_pk,user=request.user)
        if request.method == 'POST':
            #todo.delete()
            todo.delete = True;
            todo.save()
            return redirect('currenttodoss')
@login_required
def completedtodos(request):
    todos =Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    c = Todo.objects.filter(user=request.user, datecompleted__isnull=False).count()
    return render(request, 'todo/completedtodos.html',{'todos':todos,'c':c})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, EventForm, BookForm
from django.contrib import messages
from .models import Event, UserBook
from django.db.models import Q
import datetime
from datetime import date


def home(request):
    return render(request, 'home.html')

def event_list(request):
    events = Event.objects.all()
    ongoing = []
     
    for i in events:
        if i.date > date.today():
            ongoing.append(i)
        elif i.date == date.today():
            if i.time > datetime.datetime.now().time():
                ongoing.append(i)

    query = request.GET.get("q")
    if query:
        ongoing = events.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(owner__username__icontains=query)
            ).distinct()
    context = {
        "events": events,
        "ongoing": ongoing,
    }
    return render(request, 'event_list.html', context)

def my_list(request):
    events = Event.objects.filter(owner=request.user)
    userbook = UserBook.objects.all()
    time_now = datetime.datetime.now().time()
    date_now = date.today()

    query = request.GET.get("q")
    if query:
        events = events.filter(
            Q(title__icontains=query)|
            Q(description__icontains=query)|
            Q(owner__username__icontains=query)
            ).distinct()
    context = {
        "events": events,
        "userbook": userbook,
        "time_now": time_now,
        "date_now": date_now,
    }
    return render(request, 'dashboard.html', context)

def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    userbook = UserBook.objects.filter(event=event)
    

    # form = BookForm(instance=event)
    if request.method == "POST":
        seat_request2 = request.POST.get('seatsNum')
        # seat_request = request.POST.get('seats')
        if not seat_request2:
            messages.success(request, "You request empty seats")
            return redirect("event-detail",event_id)

        available = event.seats
        remaining = int(available) - int(seat_request2)
        if remaining == 0:
            messages.success(request, "No available seats")
            return redirect("event-detail",event_id)
        elif remaining < 0:
            messages.success(request, "The seats requested are above maximum capacity. There are only "+str(available)+" seats available.")
            return redirect("event-detail",event_id)
        else:
            
            # form = BookForm(request.POST,instance = event)
            # if form.is_valid:
                # event = form.save(commit=False)
            usernames = []
            # for i in userbook:
            #     usernames.append(i.user.username) 

            if request.user.username not in usernames:
                UserBook.objects.create(event=event, user=request.user, seats=seat_request2)
            # else:
            #     for j in userbook:
            #         if j.user.username == request.user.username:
            #             print(j.user.username,  request.user.username)
            #             current_user = UserBook.objects.get(id=request.user.id)
            #             print(current_user.user.username)
            #             current_user.seats += int(seat_request2)
            #             current_user.save()
            #             print(current_user.seats)
            event.seats = remaining
            
            event.save()
                # form.save()
            messages.success(request, "Event is booked successfully!")
            return redirect("event-detail",event_id)
            # else:
            #     messages.errors(request, "Event is booked successfully!")
            #     return redirect("event-detail",event_id)


                
                

    context = {
        "event": event,
        # "form": form,
        
        "userbook": userbook,
    }
    return render(request, 'event_detail.html', context)


def event_create(request):
    if request.user.is_anonymous:
        return redirect('signin')
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES or None)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            messages.success(request, "Successfully Created!")
            return redirect('home')
        print (form.errors)
    context = {
    "form": form,
    "username": "hamza",
    }
    return render(request, 'event_create.html', context)


def event_delete(request, event_id):
    if request.user.is_anonymous:
        return redirect('signin')
    event = Event.objects.get(id=event_id)
    if not request.user==event.owner:
       return redirect('no-access')

    Event.objects.get(id=event_id).delete()
    messages.success(request, "Successfully Deleted!")
    return redirect('event-list')


def event_update(request, event_id):
    if request.user.is_anonymous:
        return redirect('signin')        

    event = Event.objects.get(id=event_id)
    if not request.user==event.owner:
        return redirect('no-access')

    
    form = EventForm(instance=event)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES or None, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Edited!")
            return redirect('dashboard')
        print (form.errors)
    context = {
    "form": form,
    "event": event,
    }
    return render(request, 'event_update.html', context)







# =====================================================
class Signup(View):
    form_class = UserSignup
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            messages.success(request, "You have successfully signed up.")
            login(request, user)
            return redirect("home")
        messages.warning(request, form.errors)
        return redirect("signup")


class Login(View):
    form_class = UserLogin
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                messages.success(request, "Welcome Back!")
                return redirect('home') # ++++++++++++++++++dashboard++++++++++++++++++
            messages.warning(request, "Wrong email/password combination. Please try again.")
            return redirect("login")
        messages.warning(request, form.errors)
        return redirect("login")


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect("login")


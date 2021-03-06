from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, EventForm, BookForm, ProfileForm
from django.contrib import messages
from .models import Event, UserBook, Profile
from django.db.models import Q
import datetime
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls import url


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
    hour = -1*time_now.hour
    date_now = date.today()
    ok = False
    
    
    ################################################
    # for i in userbook:
    #     if request.user == i.user:
    #         x = i.event.time.hour - time_now.hour
    #         if x >= 3:
    #             ok.append(True)
    #         else:
    #             ok.append(False)
    # for i in ok:
    #     print(i)

    #################################################

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
        "ok": ok,
        "hour": hour,
    }
    return render(request, 'dashboard.html', context)

def book_delete(request, user_id, event_id):
    event = Event.objects.get(id=event_id)
    event.seats += UserBook.objects.get(id=user_id).seats
    event.save()

    UserBook.objects.get(id=user_id).delete()
    messages.success(request, "Event booked is successfully canceled!")
    return redirect('dashboard')



def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    userbook = UserBook.objects.filter(event=event)
    date_now = date.today()

    if request.method == "POST":
        seat_request2 = request.POST.get('seatsNum')
        if not seat_request2:
            messages.success(request, "You request empty seats, please try again.")
            return redirect("event-detail",event_id)

        available = event.seats
        remaining = int(available) - int(seat_request2)
        if available == 0:
            messages.success(request, "No available seats")
            return redirect("event-detail",event_id)
        elif remaining < 0:
            messages.success(request, "The seats requested are above maximum capacity. There are only "+str(available)+" seats available.")
            return redirect("event-detail",event_id)
        else:
            UserBook.objects.create(event=event, user=request.user, seats=seat_request2)
            event.seats = remaining           
            event.save()
            messages.success(request, "Event is booked successfully!")
            return redirect("event-detail",event_id)

    context = {
        "event": event,
        "userbook": userbook,
        "date_now": date_now,
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
    }
    return render(request, 'event_create.html', context)

def profile_info(request):  
    form = ProfileForm() 
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES or None)   
        if form.is_valid():
            profile = form.save(commit=False) 
            profile.user = request.user
            profile.save()
            return redirect('home')
    context = {
    "form": form,
     }
    return render(request, 'profile.html', context)

def profile_detail(request, profile_id):
    events = Event.objects.filter(owner=profile_id)
    try:
        profile = Profile.objects.get(id=profile_id)
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user, name = " ", bio = " ")

    context = {
        "profile": profile,
        "events": events,
    }
    return render(request, 'profile_view.html', context)


def profile_edit(request, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)

    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user, name = "X", bio = "Y")

    form = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES or None, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully Edited!")
            return redirect('home')
        print (form.errors)
    context = {
    "form": form,
    "profile": profile,
    }
    return render(request, 'profile.html', context)



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


from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    owner = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    description = models.TextField()
    date = models.DateField(auto_now=False)
    time = models.TimeField(auto_now=False)
    location = models.TextField()  
    seats = models.PositiveIntegerField(default=0)

    def __str__(self): 
        return self.title


    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'event_id':self.id})

class UserBook(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField(default=0)
    date_time = models.DateTimeField(auto_now=True)

# class MyEvent(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
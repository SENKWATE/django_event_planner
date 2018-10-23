from django.urls import path
from .views import Login, Logout, Signup, home, event_list, event_detail, event_create, event_delete, event_update, my_list, book_delete, profile_info

urlpatterns = [
	path('home', home, name='home'),
	path('home/event-list', event_list, name='event-list'),
	path('home/dashboard', my_list, name='dashboard'),
	path('home/create', event_create, name='event-create'),
	path('home/profile/', profile_info, name='profile'),

	path('home/event-list/<int:event_id>', event_detail, name='event-detail'),
	path('home/delete/<int:event_id>', event_delete, name='event-delete'),
	path('home/update/<int:event_id>', event_update, name='event-update'),
	path('home/book-delete/<int:user_id>/<int:event_id>', book_delete, name='book-delete'),

    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
]
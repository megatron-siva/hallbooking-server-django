from django.urls import path
from . import views

urlpatterns = [path('',views.register,name='register'),path('login',views.login_check,name='login_check'),path('on_change_date',views.on_change_date,name='on_change_date'),
               path('hallbooking',views.book_hall,name='book_hall'),path('requests',views.requests,name='requests'),
               path('decision',views.decision,name='decision'),path('mybookings',views.mybookings,name='mybookings'),
               path('myapprovals',views.myapprovals,name='myapprovals'),path('cancel',views.cancel,name='cancel')]
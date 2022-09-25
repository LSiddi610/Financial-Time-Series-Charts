from django.urls import path
from chart import views


urlpatterns = [
    #path('<eticker>/<position>/<entry_date>/<exit_date>/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),


]
from django.urls import path, include
from . import views

app_name = "chat"
urlpatterns = [
    
    path('', views.lobby, name='lobby'),
    path("signup/", views.authView, name="authView"),
    path('accounts/', include("django.contrib.auth.urls")),
    path('<str:username>/', views.chat_room, name='chat_room'),
]
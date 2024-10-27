from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import models
from .models import Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def lobby(request):
    users = User.objects.exclude(username=request.user.username)  # Exclude user record
    return render(request, 'chat/lobby.html', {'users': users, 'currentUser':request.user.username})

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('chat:login')
    else:       
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})









def chat_room(request, username):
    print(f"Accessing chat_room with username: {username}")
    try:
        receiver = User.objects.get(username=username)
    except User.DoesNotExist:
        print("catched")
        return redirect("chat:lobby")
    
    sender = request.user
    
    # Get all messages between the sender and receiver
    messages = Message.objects.filter(
        (models.Q(sender=sender) & models.Q(receiver=receiver)) | 
        (models.Q(sender=receiver) & models.Q(receiver=sender))
    ).order_by('timestamp')  # Ordering by timestamp

    context = {
        'username': username,
        'messages': messages
    }
    
    return render(request, 'chat/chat_room.html', context)
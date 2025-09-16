from django.shortcuts import render, redirect
from .models import Message
from django.conf import settings
import threading
import os
from agent_engine.utilities.utility import infoextractor

def home(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')

        # Save user message
        Message.objects.create(sender='user', text=user_message)

        # Dummy bot response (replace with AI logic)
        bot_response = f"You said: {user_message}"
        Message.objects.create(sender='bot', text=bot_response)

        return redirect('home')  # Redirect to avoid resubmission on refresh

    # Fetch chat history from DB
    chat_history = Message.objects.all()
    return render(request, 'home.html', {'messages': chat_history})


def file_upload_view(request):
    message = ""
    if request.method == "POST" and request.FILES.get('file'):
        upload = request.FILES['file']

        # Define upload path (make sure MEDIA_ROOT is defined in settings)
        upload_path = os.path.join(settings.MEDIA_ROOT, upload.name)

        # Save file to disk
        with open(upload_path, 'wb+') as destination:
            for chunk in upload.chunks():
                destination.write(chunk)

        threading.Thread(target=infoextractor, args=(upload_path,)).start()
        

        message = f"File '{upload.name}' uploaded successfully."

    return render(request, 'upload.html', {'message': message})

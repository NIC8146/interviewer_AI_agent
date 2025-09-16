from django.shortcuts import render, redirect
from .models import Message

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

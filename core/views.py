from django.shortcuts import render, redirect
from .models import Message, CandidateInfo
from django.conf import settings
import threading
import os
from agent_engine.utilities.utility import infoextractor

def home(request):
    return render(request, "home.html", {
        "messages": []  # if you want to preload messages later
    })


# 
def resumeInfoToDB(upload_path):
    extracted_data = infoextractor(upload_path)

    # Save extracted data to the database
    candidate = CandidateInfo.objects.create(
        name=extracted_data.name,
        age=extracted_data.age,
        email=extracted_data.email,
        skills=extracted_data.skills,
        certifications=extracted_data.Certifications,
        experience=extracted_data.experience,
        achievements=extracted_data.achievements,
        domain_knowledge=extracted_data.domain_knowledge,
        communication_skills=extracted_data.communication_skills,
        education=extracted_data.education,
        softskills=extracted_data.softskills,
        hobbies=extracted_data.hobbies,
        internships=extracted_data.internships,
        miscellaneous=extracted_data.miscellaneous
    )

def file_upload_view(request):
    message = ""
    if request.method == "POST" and request.FILES.get('file'):
        upload = request.FILES['file']

        # Clear existing files in MEDIA_ROOT
        for filename in os.listdir(settings.MEDIA_ROOT):
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Define upload path (make sure MEDIA_ROOT is defined in settings)
        upload_path = os.path.join(settings.MEDIA_ROOT, upload.name)

        # Save file to disk
        with open(upload_path, 'wb+') as destination:
            for chunk in upload.chunks():
                destination.write(chunk)

        threading.Thread(target=resumeInfoToDB, args=(upload_path,)).start()
        

        message = f"File '{upload.name}' uploaded successfully."

    return render(request, 'upload.html', {'message': message})

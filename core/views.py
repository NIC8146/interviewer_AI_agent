from django.shortcuts import render, redirect, HttpResponse
from .models import Message, CandidateInfo, candidate
from django.conf import settings
import threading
import os
from agent_engine.utilities.utility import infoextractor
from django.http import JsonResponse

def home(request, pk):

    userid = candidate.objects.filter(user_id=pk)
    if len(userid) == 0:
        return HttpResponse("Invalid User ID")
        
    return render(request, "home.html", {
        "messages": []
    })


# 
def resumeInfoToDB(upload_path, userid):
    extracted_data = infoextractor(upload_path)

    # Save extracted data to the database
    candidate = CandidateInfo.objects.create(
        user_id=userid,
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


def upload_file_view(request, pk):
    userid = candidate.objects.filter(user_id=pk)

    # Check if a resume already exists for the given user ID
    if CandidateInfo.objects.filter(user_id=userid[0]).exists():
        return JsonResponse({"message": "resume already exists"}, status=403)

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

        # Use the user ID from the URL parameter
        threading.Thread(target=resumeInfoToDB, args=(upload_path, userid[0])).start()

        return JsonResponse({"message": f"File '{upload.name}' uploaded successfully for user {pk}."})

    return JsonResponse({"message": "Invalid request."}, status=400)

def check_resume_status(request, pk):
    userid = candidate.objects.filter(user_id=pk)

    # Check if a resume already exists for the given user ID
    if CandidateInfo.objects.filter(user_id=userid[0]).exists():
        return JsonResponse({"resume_exists": True})

    return JsonResponse({"resume_exists": False})

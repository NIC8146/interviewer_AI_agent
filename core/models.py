from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # auto time
    candidate = models.ForeignKey('User', on_delete=models.CASCADE, related_name='messages', null=True, blank=True, help_text="The candidate associated with this message")

    class Meta:
        ordering = ['timestamp']  # messages show oldest → newest

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"


class CandidateInfo(models.Model):
    id = models.BigAutoField(primary_key=True)  # Unique ID and primary key
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_info', null=True, blank=True, help_text="The user associated with this candidate")
    name = models.CharField(max_length=255, null=True, blank=True, help_text="Full name of the candidate")
    age = models.IntegerField(null=True, blank=True, help_text="Age of the candidate")
    email = models.EmailField(null=True, blank=True, help_text="Email of the candidate")
    skills = models.TextField(null=True, blank=True, help_text="Summary of skills of the candidate")
    certifications = models.TextField(null=True, blank=True, help_text="Summary of certifications of the candidate")
    experience = models.TextField(null=True, blank=True, help_text="Summary of professional experience of the candidate")
    achievements = models.TextField(null=True, blank=True, help_text="Summary of achievements of the candidate")
    domain_knowledge = models.TextField(null=True, blank=True, help_text="Summary of domain knowledge of the candidate")
    communication_skills = models.TextField(null=True, blank=True, help_text="Summary of communication skills of the candidate")
    education = models.TextField(null=True, blank=True, help_text="Summary of educational background of the candidate")
    softskills = models.TextField(null=True, blank=True, help_text="Summary of soft skills of the candidate")
    hobbies = models.TextField(null=True, blank=True, help_text="Summary of hobbies of the candidate")
    internships = models.TextField(null=True, blank=True, help_text="Summary of internships of the candidate")
    miscellaneous = models.TextField(null=True, blank=True, help_text="Summary of any other relevant information about the candidate")

    def __str__(self):
        return self.name if self.name else "Unnamed Candidate"


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)  # Unique ID and primary key
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
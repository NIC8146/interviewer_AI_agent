from django.contrib import admin
from .models import Message, CandidateInfo

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'text', 'timestamp', 'candidate')
    list_filter = ('sender', 'timestamp')
    search_fields = ('text', 'candidate__name')

@admin.register(CandidateInfo)
class CandidateInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'email', 'skills', 'certifications')
    list_filter = ('age', 'domain_knowledge')
    search_fields = ('name', 'email', 'skills', 'certifications')
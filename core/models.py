from django.db import models

class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # auto time

    class Meta:
        ordering = ['timestamp']  # messages show oldest → newest

    def __str__(self):
        return f"{self.sender}: {self.text[:30]}"

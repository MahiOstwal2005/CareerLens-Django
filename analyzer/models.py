import os
from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return f"{self.user.username}'s Resume - {self.uploaded_at.date()}"

class ATSResult(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    feedback = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score: {self.score} for {self.resume}"

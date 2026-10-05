import os
from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    DOC_TYPE_CHOICES = [
        ('resume', 'Resume'),
        ('portfolio', 'Portfolio'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES, default='resume')
    file = models.FileField(upload_to='resumes/', blank=True, null=True)
    portfolio_url = models.URLField(max_length=1000, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)
    
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        elif self.portfolio_url:
            return self.portfolio_url
        return "Unknown File"
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_doc_type_display()} - {self.uploaded_at.date()}"

class ATSResult(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    matched_keywords = models.JSONField(default=list)
    missing_keywords = models.JSONField(default=list)
    feedback = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score: {self.score} for {self.resume}"

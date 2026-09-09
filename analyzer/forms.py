from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['doc_type', 'file']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select mb-3'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx'})
        }

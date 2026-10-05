from django import forms
from .models import Resume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['doc_type', 'file', 'portfolio_url']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select mb-3', 'id': 'docTypeSelect'}),
            'file': forms.FileInput(attrs={'class': 'form-control mb-3', 'accept': '.pdf,.docx,.txt,.html', 'id': 'fileInput'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control mb-3', 'placeholder': 'https://your-portfolio.com', 'id': 'urlInput'})
        }

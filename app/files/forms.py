from django import forms 
from .models import UserFile 

class UploadFileForm(forms.ModelForm): 
    class Meta: 
        model = UserFile 
        fields = ['file', 'original_name', 'description']
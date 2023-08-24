from django import forms

class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '15'}))

class EditEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '15'}))
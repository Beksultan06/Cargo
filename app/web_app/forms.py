from django import forms

class TrackingSearchForm(forms.Form):
    track = forms.CharField(
        required=False, 
        label="Трек-номер", 
        widget=forms.TextInput(attrs={'placeholder': 'Введите трек-номер'})
    )

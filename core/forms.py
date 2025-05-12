from django import forms
from core.models import User

class UserProfileForm(forms.ModelForm):
    RELATIONSHIP_STATUS_CHOICES = [
        ('', 'Select relationship status'),
        ('Dating', 'Dating'),
        ('Engaged', 'Engaged'),
        ('Married', 'Married'),
        ('Long-term partners', 'Long-term partners'),
        ('Other', 'Other'),
    ]
    
    RELATIONSHIP_DURATION_CHOICES = [
        ('', 'Select duration'),
        ('Less than 6 months', 'Less than 6 months'),
        ('6 months to 1 year', '6 months to 1 year'),
        ('1-2 years', '1-2 years'),
        ('2-5 years', '2-5 years'),
        ('5-10 years', '5-10 years'),
        ('10+ years', '10+ years'),
    ]
    
    CHALLENGE_FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Twice a week'),
    ]
    
    CATEGORY_CHOICES = [
        ('Communication Boosters', 'Communication Boosters'),
        ('Physical Touch & Affection', 'Physical Touch & Affection'),
        ('Creative Date Night Ideas', 'Creative Date Night Ideas'),
        ('Sexual Exploration', 'Sexual Exploration'),
        ('Emotional Connection', 'Emotional Connection'),
    ]
    
    partner1_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'})
    )
    
    partner2_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Partner\'s name'})
    )
    
    relationship_status = forms.ChoiceField(
        choices=RELATIONSHIP_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    relationship_duration = forms.ChoiceField(
        choices=RELATIONSHIP_DURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    challenge_frequency = forms.ChoiceField(
        choices=CHALLENGE_FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    preferred_categories = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    excluded_categories = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'partner1_name', 'partner2_name', 'relationship_status',
            'relationship_duration', 'challenge_frequency',
            'preferred_categories', 'excluded_categories'
        ]
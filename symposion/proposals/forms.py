from django import forms
from django.db.models import Q

from markitup.widgets import MarkItUpWidget

from symposion.proposals.models import PyConProposalCategory, PyConProposal


class PyConProposalForm(forms.ModelForm):
    
    class Meta:
        model = PyConProposal
        fields = [
            "title",
            "category",
            "audience_level",
            "extreme",
            "duration",
            "description",
            "abstract",
            "additional_notes",
        ]
        widgets = {
            "abstract": MarkItUpWidget(),
            "additional_notes": MarkItUpWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super(PyConProposalForm, self).__init__(*args, **kwargs)
        self.fields["category"] = forms.ModelChoiceField(
            queryset = PyConProposalCategory.objects.order_by("name")
        )
    
    def clean_description(self):
        value = self.cleaned_data["description"]
        if len(value) > 400:
            raise forms.ValidationError(
                u"The description must be less than 400 characters"
            )
        return value


class AddSpeakerForm(forms.Form):
    
    email = forms.EmailField(
        label = "Email address of new speaker (use their email address, not yours)"
    )
    
    def __init__(self, *args, **kwargs):
        self.proposal = kwargs.pop("proposal")
        super(AddSpeakerForm, self).__init__(*args, **kwargs)
    
    def clean_email(self):
        value = self.cleaned_data["email"]
        exists = self.proposal.additional_speakers.filter(
            Q(user=None, invite_email=value) |
            Q(user__email=value)
        ).exists()
        if exists:
            raise forms.ValidationError(
                "This email address has already been added to your talk proposal"
            )
        return value
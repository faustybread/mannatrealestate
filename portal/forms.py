from django import forms

from properties.models import Property, SectorMap
from .models import SellerSubmission


class MultipleFileInput(forms.ClearableFileInput):
    """Widget that accepts multiple files in one <input type='file'>."""
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """
    Form field that lets a single <input multiple> yield a list of images.

    Django's default `ImageField` calls `to_python` on a single file; here we
    map it across every uploaded file, returning a list the view can iterate
    and turn into `PropertyImage` rows.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        # Single file (edge case — normal <input> without multiple selection).
        return [single(data, initial)] if data else []


class PropertyForm(forms.ModelForm):
    """The 'idiot-proof' listing form used on the portal."""

    # A single input, styled as a big drop zone, that accepts many gallery
    # images at once. Kept out of the ModelForm meta so it can be handled
    # per-file in the view.
    gallery_images = MultipleImageField(
        required=False,
        label='Gallery images',
        help_text='Optional. Select multiple photos at once (Cmd/Ctrl-click).',
    )

    class Meta:
        model = Property
        fields = [
            'title',
            'property_type',
            'location',
            'latitude',
            'longitude',
            'price',
            'bedrooms',
            'bathrooms',
            'square_footage',
            'description',
            'primary_image',
            'is_published',
        ]
        widgets = {
            'title':          forms.TextInput(attrs={'placeholder': 'e.g. Suncity Villa, Sector 35'}),
            'location':       forms.TextInput(attrs={'placeholder': 'e.g. Sector 35, Rohtak'}),
            'latitude':       forms.NumberInput(attrs={'placeholder': '28.862345', 'step': '0.000001'}),
            'longitude':      forms.NumberInput(attrs={'placeholder': '76.587210', 'step': '0.000001'}),
            'price':          forms.NumberInput(attrs={'placeholder': '45000000', 'step': '10000', 'min': '0'}),
            'bedrooms':       forms.NumberInput(attrs={'min': '0', 'step': '1'}),
            'bathrooms':      forms.NumberInput(attrs={'min': '0', 'step': '0.5'}),
            'square_footage': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
            'description':    forms.Textarea(attrs={'rows': 6, 'placeholder': 'A concise, evocative description of the residence…'}),
        }
        labels = {
            'latitude':     'Latitude (decimal)',
            'longitude':    'Longitude (decimal)',
            'is_published': 'Publish immediately (visible on the public site)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a consistent .form-input class to every non-checkbox field so
        # the glass template can style them without per-field markup.
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check')
            elif isinstance(widget, (forms.FileInput, MultipleFileInput)):
                widget.attrs.setdefault('class', 'form-file')
            else:
                widget.attrs.setdefault('class', 'form-input')


class SectorMapForm(forms.ModelForm):
    """Upload / edit a township or sector layout map from the portal."""

    class Meta:
        model = SectorMap
        fields = ['name', 'image', 'description', 'order', 'is_published']
        widgets = {
            'name':        forms.TextInput(attrs={'placeholder': 'e.g. Suncity Rohtak'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Optional context — developer, plot count, sector notes…',
            }),
            'order':       forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }
        labels = {
            'image':        'Layout image (PNG / JPG)',
            'order':        'Display order (lower = shown first)',
            'is_published': 'Publish on the public /sitemaps/ page',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check')
            elif isinstance(widget, forms.FileInput):
                widget.attrs.setdefault('class', 'form-file')
            else:
                widget.attrs.setdefault('class', 'form-input')


class SellerSubmissionForm(forms.ModelForm):
    """Public form used on /list-property/ — submitted via AJAX."""
    class Meta:
        model = SellerSubmission
        fields = ['seller_name', 'phone', 'property_type', 'sector_location', 'size', 'expected_price', 'notes']
        widgets = {
            'seller_name':     forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'phone':           forms.TextInput(attrs={'placeholder': '+91 98765 43210'}),
            'sector_location': forms.TextInput(attrs={'placeholder': 'e.g. Sector 35, Suncity Township'}),
            'size':            forms.TextInput(attrs={'placeholder': 'e.g. 200 sq yd, 2400 sq ft'}),
            'expected_price':  forms.TextInput(attrs={'placeholder': 'e.g. ₹45 Lakh'}),
            'notes':           forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional details…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-input appearance-none cursor-pointer')
            else:
                widget.attrs.setdefault('class', 'form-input')

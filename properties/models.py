from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Property(models.Model):
    """A single luxury real-estate listing."""

    PROPERTY_TYPES = [
        ('plot',          'Plot'),
        ('villa',         'Villa'),
        ('flat',          'Flat / Apartment'),
        ('builder_floor', 'Builder Floor'),
        ('commercial',    'Commercial'),
        ('farmhouse',     'Farmhouse'),
    ]

    title = models.CharField(max_length=255)
    property_type = models.CharField(
        max_length=20, choices=PROPERTY_TYPES, default='flat', blank=True,
        help_text='Category shown on listing cards and filters.',
    )
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2)
    location = models.CharField(max_length=255)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        help_text="Half-baths supported (e.g. 3.5).",
    )
    square_footage = models.PositiveIntegerField(help_text="Interior area in sq ft.")

    # Structured list of amenities/features (e.g. ["Ocean view", "Wine cellar"]).
    features_list = models.JSONField(default=list, blank=True)

    # Geographic coordinates for the map embed on the detail page. Optional so
    # older rows and mid-listing drafts don't force us to know exact lat/lng.
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Decimal latitude, e.g. 28.862345 for a Rohtak property.",
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Decimal longitude, e.g. 76.587210 for a Rohtak property.",
    )

    primary_image = models.ImageField(upload_to='properties/primary/')

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self) -> str:
        return f"{self.title} — {self.location}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'property'
            slug = base
            n = 1
            # Ensure uniqueness — fine for the admin flow, not race-free.
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('properties:detail', kwargs={'slug': self.slug})


class PropertyImage(models.Model):
    """Additional gallery photos attached to a Property."""

    property = models.ForeignKey(
        Property,
        related_name='gallery_images',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to='properties/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return f"Image for {self.property.title} (#{self.order})"


class SectorMap(models.Model):
    """
    An uploadable, official sector / township layout map.

    Displayed on the public /sitemaps/ page as a zoomable glass gallery so
    buyers can read individual plot numbers. Admins upload these images
    themselves (Django admin or the client portal).
    """

    name = models.CharField(
        max_length=120,
        help_text="Display name — e.g. 'Suncity Rohtak' or 'Omaxe City'.",
    )
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    image = models.ImageField(
        upload_to='sector_maps/',
        blank=True,
        help_text="Official layout / sector map image. High-res PNG or JPG.",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional context — sector, developer, plot count, etc.",
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Sector Map'
        verbose_name_plural = 'Sector Maps'

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'sector-map'
            slug = base
            n = 1
            while SectorMap.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

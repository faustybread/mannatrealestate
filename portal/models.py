from django.db import models


class SellerSubmission(models.Model):
    """A property listing enquiry submitted by a seller via /list-property/."""

    PROPERTY_TYPES = [
        ('plot',        'Plot'),
        ('rental',      'Rental'),
        ('residential', 'Residential'),
        ('commercial',  'Commercial'),
    ]
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('contacted',  'Contacted'),
        ('valued',     'Valued'),
        ('closed',     'Closed'),
    ]

    seller_name    = models.CharField(max_length=200)
    phone          = models.CharField(max_length=30)
    property_type  = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    sector_location = models.CharField(max_length=200)
    size           = models.CharField(max_length=100, blank=True)
    expected_price = models.CharField(max_length=100, blank=True)
    notes          = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Seller Submission'
        verbose_name_plural = 'Seller Submissions'

    def __str__(self):
        return f"{self.seller_name} — {self.sector_location} ({self.get_status_display()})"


class SiteVisitLead(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    preferred_location = models.CharField(max_length=200)
    property_ref = models.CharField(max_length=200, blank=True, default='')
    is_contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Site Visit Lead'
        verbose_name_plural = 'Site Visit Leads'

    def __str__(self):
        return f"{self.name} — {self.preferred_location}"

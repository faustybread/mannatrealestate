from datetime import timedelta
from urllib.parse import urlencode

from django.db import models
from django.utils import timezone


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
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
    ]

    # A site visit is assumed to last one hour when placed on a calendar.
    VISIT_DURATION = timedelta(hours=1)

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    preferred_location = models.CharField(max_length=200)
    preferred_datetime = models.DateTimeField(null=True, blank=True)
    property_ref = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Site Visit Lead'
        verbose_name_plural = 'Site Visit Leads'

    def __str__(self):
        return f"{self.name} — {self.preferred_location}"

    # ── Calendar helpers ──────────────────────────────────────────────
    @property
    def visit_end(self):
        """End time of the scheduled visit (start + 1h), or None if unscheduled."""
        if self.preferred_datetime:
            return self.preferred_datetime + self.VISIT_DURATION
        return None

    @property
    def event_title(self):
        return f"Site Visit — {self.name} ({self.preferred_location})"

    @property
    def event_details(self):
        lines = [
            f"Site visit booked via MR Estates.",
            f"Name: {self.name}",
            f"Phone: {self.phone}",
            f"Preferred location: {self.preferred_location}",
        ]
        if self.property_ref:
            lines.append(f"Property ref: {self.property_ref}")
        return "\n".join(lines)

    @staticmethod
    def _cal_stamp(dt):
        """Format a datetime as UTC basic form for calendars: 20260720T153000Z."""
        return dt.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    @property
    def google_calendar_url(self):
        """One-click 'Add to Google Calendar' link. Empty if no date was chosen."""
        if not self.preferred_datetime:
            return ''
        params = {
            'action': 'TEMPLATE',
            'text': self.event_title,
            'dates': f"{self._cal_stamp(self.preferred_datetime)}/{self._cal_stamp(self.visit_end)}",
            'details': self.event_details,
            'location': self.preferred_location,
        }
        return 'https://calendar.google.com/calendar/render?' + urlencode(params)

    @property
    def ics_content(self):
        """A downloadable .ics event (Apple Calendar, Outlook, etc.)."""
        if not self.preferred_datetime:
            return ''

        def esc(text):
            return (text.replace('\\', '\\\\').replace(',', '\\,')
                        .replace(';', '\\;').replace('\n', '\\n'))

        return "\r\n".join([
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//MR Estates//Site Visit//EN',
            'CALSCALE:GREGORIAN',
            'BEGIN:VEVENT',
            f'UID:site-visit-{self.pk}@mrestates',
            f'DTSTAMP:{self._cal_stamp(timezone.now())}',
            f'DTSTART:{self._cal_stamp(self.preferred_datetime)}',
            f'DTEND:{self._cal_stamp(self.visit_end)}',
            f'SUMMARY:{esc(self.event_title)}',
            f'DESCRIPTION:{esc(self.event_details)}',
            f'LOCATION:{esc(self.preferred_location)}',
            'END:VEVENT',
            'END:VCALENDAR',
        ])

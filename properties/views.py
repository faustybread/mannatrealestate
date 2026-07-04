from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from .models import Property, SectorMap


def homepage(request):
    """Public landing page — a curated selection of published listings."""
    featured = Property.objects.filter(is_published=True)[:6]
    return render(
        request,
        'properties/homepage.html',
        {'featured_properties': featured},
    )


# Price brackets exposed to the filter UI.  (value posted, label shown)
# Amounts are in INR — sized to the Rohtak market: sub-crore flats and
# builder floors on the low end, multi-crore Suncity villas at the top.
PRICE_BRACKETS = [
    ('',                    'Any budget'),
    ('0-7500000',           'Up to ₹75 L'),
    ('7500000-15000000',    '₹75 L – ₹1.5 Cr'),
    ('15000000-30000000',   '₹1.5 Cr – ₹3 Cr'),
    ('30000000-50000000',   '₹3 Cr – ₹5 Cr'),
    ('50000000-',           '₹5 Cr and above'),
]


def _apply_filters(qs, params):
    """Narrow a Property queryset by GET params. Returns (queryset, active_filters_dict)."""
    active = {}

    location = (params.get('location') or '').strip()
    if location:
        qs = qs.filter(location__icontains=location)
        active['location'] = location

    bedrooms = (params.get('bedrooms') or '').strip()
    if bedrooms.isdigit():
        n = int(bedrooms)
        # "6+" behaviour — treat as a floor.
        qs = qs.filter(bedrooms__gte=n) if n >= 6 else qs.filter(bedrooms=n)
        active['bedrooms'] = bedrooms

    bracket = (params.get('price') or '').strip()
    if bracket and '-' in bracket:
        lo_s, hi_s = bracket.split('-', 1)
        try:
            if lo_s:
                qs = qs.filter(price__gte=Decimal(lo_s))
            if hi_s:
                qs = qs.filter(price__lt=Decimal(hi_s))
            active['price'] = bracket
        except (ValueError, ArithmeticError):
            pass

    return qs, active


def property_list(request):
    """Full catalogue with glass-panel filtering."""
    qs = Property.objects.filter(is_published=True)
    filtered, active = _apply_filters(qs, request.GET)

    # Distinct locations, for a nice datalist auto-complete on the filter.
    known_locations = list(
        Property.objects.filter(is_published=True)
        .values_list('location', flat=True).distinct().order_by('location')
    )

    context = {
        'properties':      filtered,
        'total_count':     filtered.count(),
        'active_filters':  active,
        'price_brackets':  PRICE_BRACKETS,
        'known_locations': known_locations,
    }
    return render(request, 'properties/list.html', context)


def property_detail(request, slug):
    """Single-listing detail page."""
    property_obj = get_object_or_404(
        Property.objects.prefetch_related('gallery_images'),
        slug=slug,
        is_published=True,
    )
    # A small "you may also like" strip (up to 3 others in same location or price band).
    price_range = property_obj.price * Decimal('0.7'), property_obj.price * Decimal('1.3')
    related = (
        Property.objects.filter(is_published=True)
        .exclude(pk=property_obj.pk)
        .filter(location=property_obj.location)[:3]
    )
    if related.count() < 3:
        # Backfill with price-similar listings.
        backfill = (
            Property.objects.filter(is_published=True, price__range=price_range)
            .exclude(pk=property_obj.pk)
            .exclude(pk__in=[p.pk for p in related])[: 3 - related.count()]
        )
        related = list(related) + list(backfill)
    return render(
        request,
        'properties/detail.html',
        {'property': property_obj, 'related_properties': related},
    )


# Curated sector maps sourced from public real estate portals.
# These display on /sitemaps/ alongside any maps uploaded via the portal.
CURATED_SECTOR_MAPS = [
    {
        'name': 'Suncity Township — Rohtak',
        'description': 'Official layout plan for Suncity Township, Sector 35, Rohtak. One of Rohtak\'s most premium gated developments featuring residential plots, villas, and SCO commercial blocks.',
        'image_url': 'https://dynamic.realestateindia.com/proj_images/project39903/proj_img-39903-91483_2-770x400.jpg',
        'tag': 'Township Layout',
        'developer': 'Suncity Projects',
    },
    {
        'name': 'Omaxe City — Rohtak',
        'description': 'Master plan for Omaxe City, Sector 22D, Rohtak. Plotted development with wide 60-ft and 80-ft sector roads, parks, schools, and a dedicated commercial zone.',
        'image_url': 'https://www.omaxe.com/projectmasterplans/master_plan_1572341084575.jpg',
        'tag': 'Master Plan',
        'developer': 'Omaxe Ltd.',
    },
    {
        'name': 'HUDA Sectors — Rohtak (City Map)',
        'description': 'Haryana Urban Development Authority sector index map for Rohtak, showing all numbered sectors (1–35) with sector boundaries, main roads, and key landmarks.',
        'image_url': 'https://www.omaxe.com/projectmasterplans/master_plan_1570251966481.jpg',
        'tag': 'City Sector Map',
        'developer': 'HUDA / HSVP',
    },
    {
        'name': 'DDJAY Plot Scheme — Rohtak',
        'description': 'Deen Dayal Jan Awas Yojana (Affordable Plotted Housing) scheme map for Rohtak district — government-approved plotted scheme with subsidised pricing for affordable housing.',
        'image_url': 'https://www.omaxe.com/projectsiteplans/site_plan_1570251966548.jpg',
        'tag': 'DDJAY Scheme',
        'developer': 'Haryana Govt.',
    },
]


def sector_maps(request):
    """Public 'Sector Mappings' page — glass gallery of township layout maps."""
    db_maps = SectorMap.objects.filter(is_published=True)
    return render(
        request,
        'properties/sitemaps.html',
        {
            'sector_maps': db_maps,
            'curated_maps': CURATED_SECTOR_MAPS,
        },
    )


# Leadership roster shown on /about/. Hardcoded rather than DB-backed because
# the founders' cards are integral to the brand story and shouldn't be edited
# through the general property portal. Portrait IDs are stable Unsplash refs
# — resized at fetch time via URL query params.
LEADERSHIP = [
    {
        'name': 'Manish Garg',
        'role': 'Managing Director',
        'tagline': '17+ years in luxury real estate',
        'bio': (
            "Manish leads MR Estates with more than seventeen years of hands-on "
            "experience across Rohtak's luxury residential and commercial markets. "
            "He personally oversees every acquisition and represents the firm on "
            "landmark Suncity and Omaxe City transactions."
        ),
        'portrait_id': 'photo-1560250097-0b93528c311a',
        'featured': True,
    },
    {
        'name': 'Amit Garg',
        'role': 'Partner',
        'tagline': 'Investments & Client Advisory',
        'bio': (
            "Amit anchors client advisory and long-hold investment portfolios, "
            "working with families and NRIs looking to enter the Rohtak market with "
            "verified, RERA-compliant assets."
        ),
        'portrait_id': 'photo-1507003211169-0a1dd7228f2d',
        'featured': False,
    },
    {
        'name': 'Kamal Bansal',
        'role': 'Partner',
        'tagline': 'Commercial & Township Deals',
        'bio': (
            "Kamal specialises in commercial plots, showroom leasing, and township "
            "layouts. He is the team's authority on Omaxe City and Suncity master "
            "plans and negotiates the firm's largest deals."
        ),
        'portrait_id': 'photo-1519085360753-af0119f7cbe7',
        'featured': False,
    },
]


def about(request):
    """The 'About MR Estates' page — brand story, leadership, RERA compliance."""
    return render(
        request,
        'properties/about.html',
        {'leadership': LEADERSHIP},
    )


# Key investment zones displayed on the /site-visit/ interactive map.
ROHTAK_ZONES = [
    {
        'name': 'Suncity Township',
        'subtitle': 'Sector 35, Rohtak',
        'description': 'Rohtak\'s flagship luxury township — premium villas, builder floors, and SCO plots.',
        'lat': 28.9086,
        'lng': 76.5820,
        'type': 'township',
    },
    {
        'name': 'Omaxe City',
        'subtitle': 'Sector 22D, Rohtak',
        'description': 'Modern plotted development with wide sectors, parks, and excellent connectivity.',
        'lat': 28.8939,
        'lng': 76.5928,
        'type': 'township',
    },
    {
        'name': 'HUDA Sector 4',
        'subtitle': 'Premium Plots & Villas',
        'description': 'Well-established HUDA sector with premium residential plots and independent houses.',
        'lat': 28.8971,
        'lng': 76.5989,
        'type': 'huda',
    },
    {
        'name': 'HUDA Sector 14',
        'subtitle': 'Builder Floors & Flats',
        'description': 'Sought-after location for modern builder floors with strong rental yields.',
        'lat': 28.8833,
        'lng': 76.5823,
        'type': 'huda',
    },
    {
        'name': 'MR Estates Office',
        'subtitle': 'SCO 75, Suncity Business Center',
        'description': 'Our head office — visit us Mon–Sat, 10:00–19:00 IST.',
        'lat': 28.9083,
        'lng': 76.5815,
        'type': 'office',
    },
]


def site_visit_page(request):
    """Dedicated immersive site-visit booking page with interactive Rohtak map."""
    import json
    return render(
        request,
        'properties/site_visit.html',
        {'rohtak_zones_json': json.dumps(ROHTAK_ZONES)},
    )


def list_property_page(request):
    """Public /list-property/ page — multi-step seller submission form."""
    return render(request, 'properties/list_property.html')


# Demo plot data for the Omaxe City 'God View' interactive layout.
OMAXE_PLOTS = [
    {'id': 'A-1',  'size': '200 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'A-2',  'size': '150 sq yd', 'facing': 'North', 'status': 'sold'},
    {'id': 'A-3',  'size': '200 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'A-4',  'size': '250 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'A-5',  'size': '150 sq yd', 'facing': 'East',  'status': 'booked'},
    {'id': 'B-1',  'size': '200 sq yd', 'facing': 'East',  'status': 'available'},
    {'id': 'B-2',  'size': '300 sq yd', 'facing': 'East',  'status': 'available'},
    {'id': 'B-3',  'size': '200 sq yd', 'facing': 'North', 'status': 'sold'},
    {'id': 'B-4',  'size': '150 sq yd', 'facing': 'West',  'status': 'available'},
    {'id': 'B-5',  'size': '250 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'C-1',  'size': '200 sq yd', 'facing': 'South', 'status': 'booked'},
    {'id': 'C-2',  'size': '150 sq yd', 'facing': 'East',  'status': 'available'},
    {'id': 'C-3',  'size': '300 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'C-4',  'size': '200 sq yd', 'facing': 'West',  'status': 'sold'},
    {'id': 'C-5',  'size': '250 sq yd', 'facing': 'East',  'status': 'available'},
    {'id': 'D-1',  'size': '150 sq yd', 'facing': 'North', 'status': 'available'},
    {'id': 'D-2',  'size': '200 sq yd', 'facing': 'East',  'status': 'available'},
    {'id': 'D-3',  'size': '300 sq yd', 'facing': 'South', 'status': 'booked'},
    {'id': 'D-4',  'size': '150 sq yd', 'facing': 'West',  'status': 'available'},
    {'id': 'D-5',  'size': '200 sq yd', 'facing': 'North', 'status': 'sold'},
]


def omaxe_city_plot_layout(request):
    """Interactive 'God View' plot map for Omaxe City, Rohtak."""
    import json
    available = sum(1 for p in OMAXE_PLOTS if p['status'] == 'available')
    return render(request, 'properties/plot_layout.html', {
        'plots_json': json.dumps(OMAXE_PLOTS),
        'available_count': available,
        'total_count': len(OMAXE_PLOTS),
        'project_name': 'Omaxe City — Sector 22D, Rohtak',
    })

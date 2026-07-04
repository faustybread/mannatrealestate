"""
Seed the database with realistic Rohtak (Haryana) properties for MR Estates.

Wipes any previous placeholder listings and inserts a fresh curated set of
Rohtak-based properties: a Suncity Township villa, a Sector 2 builder floor,
an Omaxe City commercial plot, and a modern Sector 36A flat. Prices are in
INR — the Django template layer renders them as ₹XX Cr / ₹XX L.

Usage::

    python manage.py seed_properties            # wipe + seed everything
    python manage.py seed_properties --keep     # only add missing listings
    python manage.py seed_properties --no-images  # skip Unsplash fetch

The image fetch is intentionally best-effort: a network failure leaves the
row imageless rather than breaking the seed run, which lets the command be
used offline for local development.
"""
from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from properties.models import Property, PropertyImage, SectorMap


# ── Seed data ─────────────────────────────────────────────────
# Prices are the full rupee amount (no shorthand). The `inr` template
# filter compresses them to `₹4.5 Cr` / `₹85 L` for display.

@dataclass
class Seed:
    title: str
    location: str
    price: str                         # Decimal-string, avoids float drift.
    bedrooms: int
    bathrooms: str
    square_footage: int                # Reused as sq. yd. for the plot listing.
    description: str
    features: List[str]
    primary_photo_id: str
    # Approximate Rohtak coordinates — good enough for the Google Maps embed
    # to centre on the correct neighbourhood.
    latitude: str = ""
    longitude: str = ""
    gallery_photo_ids: List[str] = field(default_factory=list)


SEEDS: List[Seed] = [
    Seed(
        title="Suncity Signature Villa · Sector 35",
        location="Suncity Township, Sector 35, Rohtak",
        price="45000000",                # ₹4.5 Cr
        bedrooms=5, bathrooms="5.5", square_footage=4200,
        description=(
            "A double-height corner villa inside Suncity Township, one of Rohtak's most "
            "gated luxury addresses. West-facing plot with a landscaped 900 sq. ft. front "
            "lawn, imported Italian marble flooring on the ground floor, and a private lift "
            "connecting all four levels.\n\n"
            "Five bedroom suites — each with walk-in wardrobes and modular attached baths — "
            "are laid out across the first and second floors. The stilt level accommodates "
            "three cars plus staff quarters. Fully Vaastu-compliant, freshly repainted, and "
            "handed over on ready-to-move-in basis."
        ),
        features=[
            "Corner plot, 300 sq. yd.",
            "Private lift (all 4 levels)",
            "Modular kitchen with island counter",
            "Italian marble on ground floor",
            "3-car stilt parking + staff quarters",
            "24×7 gated security & power backup",
            "Vaastu-compliant layout",
        ],
        primary_photo_id="photo-1613490493576-7fde63acd811",
        latitude="28.862345", longitude="76.587210",
        gallery_photo_ids=[
            "photo-1600585154340-be6161a56a0c",
            "photo-1600607687939-ce8a6c25118c",
            "photo-1600566753086-00f18fb6b3ea",
            "photo-1600585154526-990dced4db0d",
        ],
    ),
    Seed(
        title="Independent Builder Floor · Sector 2",
        location="Sector 2, Rohtak",
        price="8500000",                 # ₹85 L
        bedrooms=3, bathrooms="3.0", square_footage=1650,
        description=(
            "A newly-constructed second-floor builder unit on a well-established Sector 2 "
            "street, walking distance from the sector market and PGIMS. Sunlit 3 BHK layout "
            "with a wide balcony overlooking a park, semi-modular kitchen, and covered stilt "
            "parking for one car.\n\n"
            "The builder has used branded fittings throughout — Kohler in the master bath, "
            "Havells wiring, and a Rhinox-treated main door. Registry-ready and available on "
            "immediate possession."
        ),
        features=[
            "Second floor, 3 BHK + study",
            "Park-facing wide balcony",
            "Semi-modular kitchen",
            "Kohler sanitary in master bath",
            "Covered stilt parking",
            "Registry-ready · Immediate possession",
        ],
        primary_photo_id="photo-1560448204-e02f11c3d0e2",
        latitude="28.900612", longitude="76.580844",
        gallery_photo_ids=[
            "photo-1502672260266-1c1ef2d93688",
            "photo-1600210492486-724fe5c67fb0",
            "photo-1600596542815-ffad4c1539a9",
        ],
    ),
    Seed(
        title="Commercial Plot · Omaxe City",
        location="Omaxe City, Rohtak",
        price="12500000",                # ₹1.25 Cr
        bedrooms=0, bathrooms="0.0", square_footage=250,     # 250 sq. yd. plot
        description=(
            "A 250 sq. yd. corner commercial plot inside Omaxe City, fronting the internal "
            "high-street. Sanctioned for retail / showroom use with a stilt + 3-floor build-"
            "up allowance under the Omaxe township master plan.\n\n"
            "Freehold, litigation-free, and located just off the Delhi Bypass — ideal for "
            "brand showrooms, clinics, or a mixed-use commercial block. All internal roads, "
            "underground utilities, and streetlighting are already commissioned."
        ),
        features=[
            "250 sq. yd. corner plot",
            "Commercial (retail / showroom) use",
            "Stilt + 3 floors sanctioned",
            "Freehold · Litigation-free",
            "High-street facing · Omaxe City",
            "Fully developed township infrastructure",
        ],
        primary_photo_id="photo-1449844908441-8829872d2607",
        latitude="28.841924", longitude="76.558070",
        gallery_photo_ids=[
            "photo-1568605114967-8130f3a36994",
            "photo-1512917774080-9991f1c4c750",
        ],
    ),
    Seed(
        title="Modern 3 BHK Flat · Sector 36A",
        location="Sector 36A, Rohtak",
        price="7200000",                 # ₹72 L
        bedrooms=3, bathrooms="2.5", square_footage=1420,
        description=(
            "A contemporary 3 BHK flat on the seventh floor of a lift-enabled apartment "
            "complex in Sector 36A. Open-plan living-dining opens to a wide balcony with "
            "an unobstructed north-east view; modular kitchen with hob and chimney is "
            "already installed.\n\n"
            "The tower features 100% power backup, two high-speed lifts, a rooftop clubhouse, "
            "and covered parking. Close to Rohtak Ring Road and the upcoming metro corridor — "
            "well suited to young families and end-users."
        ),
        features=[
            "3 BHK · 7th floor · 1,420 sq. ft.",
            "Modular kitchen (hob + chimney)",
            "Wide north-east facing balcony",
            "2 high-speed lifts, 100% backup",
            "Rooftop clubhouse & gym",
            "Covered parking, 1 car",
        ],
        primary_photo_id="photo-1600607687644-c7171b42498f",
        latitude="28.857012", longitude="76.585330",
        gallery_photo_ids=[
            "photo-1600585152220-90363fe7e115",
            "photo-1512918728675-ed5a9ecdebfd",
            "photo-1600585154363-67eb9e2e2099",
        ],
    ),
]


# Placeholder sector maps — the two headline townships. Rows exist so the
# public /sitemaps/ page has empty upload slots waiting for the admin's PNGs.
SECTOR_MAP_SEEDS = [
    {
        'name': 'Suncity Rohtak',
        'description': (
            'Official layout map of Suncity Township, Sector 35, Rohtak — plot '
            'numbers, sector roads, and green belts.'
        ),
        'order': 10,
    },
    {
        'name': 'Omaxe City',
        'description': (
            'Official Omaxe City, Rohtak master layout — residential clusters, '
            'commercial high-street, and internal road grid.'
        ),
        'order': 20,
    },
]


UNSPLASH_URL = "https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}&q={q}"


def _fetch(photo_id: str, *, width: int = 1600, quality: int = 80, timeout: int = 20) -> bytes:
    """Download a single Unsplash image, returning raw bytes."""
    url = UNSPLASH_URL.format(pid=photo_id, w=width, q=quality)
    req = urllib.request.Request(url, headers={'User-Agent': 'MREstates-Seeder/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


class Command(BaseCommand):
    help = 'Wipe placeholder listings and seed realistic Rohtak properties for MR Estates.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep', action='store_true',
            help="Don't wipe existing properties; only insert those missing by slug.",
        )
        parser.add_argument(
            '--no-images', action='store_true',
            help='Skip the Unsplash image download entirely (fast, offline-safe).',
        )
        parser.add_argument(
            '--width', type=int, default=1600,
            help='Requested Unsplash image width (default: 1600).',
        )

    def handle(self, *args, **opts):
        # ── Wipe existing rows unless --keep was passed ─────────
        # Default behaviour is a full reset — that's what "clear the previous
        # placeholder properties and seed new ones" asks for.
        if not opts['keep']:
            n, _ = Property.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f"Cleared {n} existing property row(s) (including any prior placeholders)."
            ))

        created = updated = skipped = 0
        for seed in SEEDS:
            slug = slugify(seed.title)

            prop, was_created = Property.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': seed.title,
                    'location': seed.location,
                    'price': Decimal(seed.price),
                    'bedrooms': seed.bedrooms,
                    'bathrooms': Decimal(seed.bathrooms),
                    'square_footage': seed.square_footage,
                    'description': seed.description,
                    'features_list': seed.features,
                    'latitude':  Decimal(seed.latitude)  if seed.latitude  else None,
                    'longitude': Decimal(seed.longitude) if seed.longitude else None,
                    'is_published': True,
                },
            )

            # If we're in --keep mode and the row already had an image, skip.
            if not was_created and prop.primary_image:
                skipped += 1
                self.stdout.write(f"  ↷ Skipped (already seeded): {prop.title}")
                continue

            if opts['no_images']:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Created (no image): {prop.title}"
                ))
                created += 1 if was_created else 0
                updated += 0 if was_created else 1
                continue

            # ── Primary image ──────────────────────────────
            try:
                primary_bytes = _fetch(seed.primary_photo_id, width=opts['width'])
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                self.stderr.write(self.style.WARNING(
                    f"  ! Primary image fetch failed for '{seed.title}' ({e}); "
                    f"row kept without image."
                ))
            else:
                prop.primary_image.save(
                    f"{slug}.jpg",
                    ContentFile(primary_bytes),
                    save=True,
                )

            # ── Gallery images ─────────────────────────────
            for idx, pid in enumerate(seed.gallery_photo_ids):
                try:
                    data = _fetch(pid, width=opts['width'])
                except (urllib.error.URLError, TimeoutError, OSError) as e:
                    self.stderr.write(self.style.WARNING(
                        f"    (gallery {idx} skipped: {e})"
                    ))
                    continue
                img = PropertyImage(property=prop, order=idx)
                img.image.save(f"{slug}-{idx+1}.jpg", ContentFile(data), save=True)

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Created: {prop.title} ({prop.gallery_images.count()} gallery images)"
                ))
            else:
                updated += 1
                self.stdout.write(f"  ↻ Updated: {prop.title}")

        # ── Sector-map placeholders ────────────────────────────
        # Only creates rows; never overwrites images an admin uploaded.
        for spec in SECTOR_MAP_SEEDS:
            obj, made = SectorMap.objects.get_or_create(
                name=spec['name'],
                defaults={
                    'description': spec['description'],
                    'order': spec['order'],
                    'is_published': True,
                },
            )
            if made:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Sector map placeholder: {obj.name}"
                ))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {created}  Updated: {updated}  Skipped: {skipped}"
        ))

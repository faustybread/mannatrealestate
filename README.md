# MR Estates — Mannat Real Estate

> A full-stack luxury real estate platform for Rohtak, Haryana. Built with Django 4.2, Tailwind CSS, and a glassmorphic design language across every surface.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
  - [Public Site](#public-site)
  - [Owner Portal](#owner-portal)
- [Data Models](#data-models)
- [URL Reference](#url-reference)
- [Getting Started](#getting-started)
- [Media & Assets](#media--assets)
- [Design System](#design-system)
- [Portal Credentials](#portal-credentials)

---

## Overview

MR Estates is a bespoke real estate website for **Mannat Real Estate**, a luxury agency operating across Rohtak's premium residential and commercial developments — Suncity Township, Omaxe City, HUDA sectors, and farmhouse plots on the outskirts.

The platform serves two audiences:

| Audience | Entry point | Purpose |
|---|---|---|
| **Buyers / Investors** | Public site `/` | Browse listings, view maps, book site visits |
| **Sellers** | `/list-property/` | Submit properties for a free valuation |
| **Agency owner** | `/portal/` | Manage inventory, review leads |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 (Python 3.9) |
| Database | SQLite (development) |
| Styling | Tailwind CSS via `django-tailwind` |
| Image handling | Pillow |
| Frontend maps | Leaflet.js (site visit page) |
| Media | Served via Django dev server (`MEDIA_URL`) |
| Fonts | Inter + Manrope (Google Fonts) |

---

## Project Structure

```
realestate/
├── luxury_realestate/          # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── properties/                 # Public-facing app
│   ├── models.py               # Property, PropertyImage, SectorMap
│   ├── views.py                # All public page views + AJAX endpoints
│   ├── urls.py
│   ├── templatetags/
│   │   └── rupees.py           # ₹ formatting template filter
│   └── management/commands/
│       └── seed_properties.py  # Dev seed command
│
├── portal/                     # Owner-only admin app
│   ├── models.py               # SiteVisitLead, SellerSubmission
│   ├── views.py                # Dashboard, property CRUD, leads
│   ├── forms.py                # PropertyForm, SectorMapForm, SellerSubmissionForm
│   └── urls.py
│
├── templates/
│   ├── base.html               # Global layout, navbar, footer
│   ├── properties/
│   │   ├── homepage.html       # Hero, featured listings, about strip
│   │   ├── list.html           # Filtered listing catalogue
│   │   ├── detail.html         # Single property page
│   │   ├── sitemaps.html       # Sector map gallery
│   │   ├── about.html          # Agency story, leadership, RERA info
│   │   ├── site_visit.html     # Interactive Leaflet map + booking form
│   │   ├── list_property.html  # 3-step seller submission form
│   │   └── plot_layout.html    # God View interactive plot grid
│   └── portal/
│       ├── base.html           # Portal layout + nav
│       ├── dashboard.html      # Inventory table, metric cards, lead counts
│       ├── property_form.html  # Add / Edit listing form
│       ├── sector_map_form.html
│       ├── sector_map_list.html
│       ├── leads.html          # Site visit enquiries
│       └── seller_leads.html   # Seller submission CRM
│
├── theme/                      # django-tailwind app
│   ├── static/
│   │   ├── css/dist/styles.css # Compiled Tailwind output
│   │   └── img/logo.png        # MR Estates logo (served as static)
│   └── static_src/
│       └── tailwind.config.js
│
├── media/                      # User-uploaded files (gitignored)
│   ├── properties/             # Primary + gallery images per listing
│   ├── sector_maps/            # Uploaded layout maps
│   ├── office/                 # Agency office photos (AVIF)
│   └── logo.png                # Source logo file
│
├── manage.py
└── requirements.txt
```

---

## Features

### Public Site

#### Hero & Homepage (`/`)
- Full-viewport **autoplay video** background (Pexels CDN) with a smooth fade-in on `canplay` — no poster flash
- Glassmorphic search / filter bar (location, bedrooms, price bracket)
- **Featured listings** grid — up to 6 published properties
- **About the agency** strip with real office photos
- Scroll-reveal animations on all sections (`IntersectionObserver`, `data-delay`)
- WhatsApp floating button + sticky contact bar in footer

#### Property Catalogue (`/properties/`)
- Full paginated listing of all published properties
- **Filter by:** location, bedrooms (1–6+), price bracket (₹75L up to ₹5Cr+)
- Champagne pill chips for active filters with individual clear buttons
- Listing cards show: primary image, type badge, price (formatted in Lakhs/Crores), BHK, sqft

#### Property Detail (`/properties/<slug>/`)
- Hero primary image with glassmorphic overlay
- Full description, price, BHK, bathrooms, area, property type
- **Feature tags** rendered from a JSON list
- **Gallery lightbox** — all secondary images
- Related listings strip (same location, then price-similar fallback)
- Embedded Leaflet map with marker (when lat/lng set)

#### Sector Maps (`/sitemaps/`)
- Two-section gallery:
  - **Curated maps** — internet-sourced master plans (Suncity, Omaxe City, HUDA, DDJAY)
  - **Uploaded maps** — layout images the owner uploads via portal
- Each card is zoomable with a lightbox
- `onerror` fallback for broken image URLs

#### About (`/about/`)
- Agency brand story
- Leadership team cards with portraits (Unsplash)
- RERA compliance and verification section

#### Site Visit & Contact (`/site-visit/`)
- **Interactive Leaflet.js map** centred on Rohtak
- Colour-coded markers: townships (champagne), HUDA sectors (blue), office (red)
- Clickable markers open glassmorphic popups with location details
- Booking form — **AJAX submit** (no page reload), success animation
- Lead saved to `SiteVisitLead` model

#### List Your Property (`/list-property/`)
- **3-step Apple-style glassmorphic form:**
  1. Seller name, phone, property type
  2. Sector/location, size/dimensions, notes
  3. Expected price + live summary recap of all fields
- Per-step validation with red ring on empty required fields
- Step progress indicator with animated champagne dots
- **AJAX submit** → `SellerSubmission` model
- Smooth success screen with animated checkmark on completion

#### Omaxe City Plot Layout (`/projects/omaxe-city/`)
- **"God View" interactive SVG-style plot grid** — 4 rows × 5 columns (20 plots)
- Plots colour-coded by status:
  - **Available** — champagne outlined, glow on hover
  - **Booked** — amber tint, dimmed
  - **Sold** — greyed out
- Hover any available plot → floating **glassmorphic tooltip** shows plot number, size, facing direction, status, and a "Book Site Visit" CTA
- Road overlay, compass indicator, availability counter

---

### Owner Portal

Access at `/portal/` — login required.

**Default credentials:**
```
Username: concierge
Password: mannat@2024
```

#### Dashboard (`/portal/`)
- Metric cards: Total listings, Published, Drafts, Portfolio value
- **Site Visit leads** summary with unread count → links to full list
- **Seller Submissions** summary with new-submission count → links to full list
- Full inventory table with Edit and Delete per listing

#### Manage Inventory
- **Add listing** (`/portal/properties/new/`) — full form with all fields including property type
- **Edit listing** (`/portal/properties/<slug>/edit/`) — pre-filled form
- **Delete listing** (`/portal/properties/<slug>/delete/`) — POST with confirm dialog

#### Sector Maps (`/portal/sector-maps/`)
- Upload, edit, and delete layout maps
- Uploaded maps appear on the public `/sitemaps/` page

#### Site Visit Leads (`/portal/leads/`)
- Table of all booking enquiries
- Mark as contacted with one click

#### Seller Leads (`/portal/seller-leads/`)
- All seller submissions from `/list-property/`
- Per-row: seller name, property type, location, size/price
- **Direct call button** (`tel:` link)
- **WhatsApp button** — opens WhatsApp with a pre-filled message referencing the seller's name and location
- **Inline status dropdown** (Pending → Contacted → Valued → Closed) — updates on change, no page reload needed
- Glowing champagne dot for pending submissions

---

## Data Models

### `properties` app

```
Property
  title              CharField
  property_type      CharField  choices: Plot, Villa, Flat, Builder Floor, Commercial, Farmhouse
  slug               SlugField  auto-generated, unique
  description        TextField
  price              DecimalField
  location           CharField
  bedrooms           PositiveIntegerField
  bathrooms          DecimalField  (supports half-baths)
  square_footage     PositiveIntegerField
  features_list      JSONField   list of amenity strings
  latitude           DecimalField  optional
  longitude          DecimalField  optional
  primary_image      ImageField  → media/properties/primary/
  is_published       BooleanField
  created_at         DateTimeField
  updated_at         DateTimeField

PropertyImage
  property           ForeignKey → Property (cascade)
  image              ImageField  → media/properties/gallery/
  caption            CharField
  order              PositiveIntegerField

SectorMap
  name               CharField
  slug               SlugField  auto-generated, unique
  image              ImageField  → media/sector_maps/
  description        TextField
  order              PositiveIntegerField
  is_published       BooleanField
```

### `portal` app

```
SiteVisitLead
  name               CharField
  phone              CharField
  preferred_location CharField
  property_ref       CharField  optional
  is_contacted       BooleanField
  created_at         DateTimeField

SellerSubmission
  seller_name        CharField
  phone              CharField
  property_type      CharField  choices: Plot, Rental, Residential, Commercial
  sector_location    CharField
  size               CharField  optional
  expected_price     CharField  optional
  notes              TextField  optional
  status             CharField  choices: Pending, Contacted, Valued, Closed
  created_at         DateTimeField
```

---

## URL Reference

### Public

| URL | View | Description |
|---|---|---|
| `/` | `homepage` | Landing page |
| `/properties/` | `property_list` | Filtered catalogue |
| `/properties/<slug>/` | `property_detail` | Single listing |
| `/sitemaps/` | `sector_maps` | Sector map gallery |
| `/about/` | `about` | Agency story |
| `/site-visit/` | `site_visit_page` | Interactive map + booking |
| `/list-property/` | `list_property_page` | Seller submission form |
| `/projects/omaxe-city/` | `omaxe_city_plot_layout` | God View plot map |

### Portal (login required)

| URL | View | Description |
|---|---|---|
| `/portal/` | `dashboard` | Main dashboard |
| `/portal/login/` | `PortalLoginView` | Login |
| `/portal/logout/` | `PortalLogoutView` | Logout |
| `/portal/properties/new/` | `property_new` | Add listing |
| `/portal/properties/<slug>/edit/` | `property_edit` | Edit listing |
| `/portal/properties/<slug>/delete/` | `property_delete` | Delete listing |
| `/portal/sector-maps/` | `sector_map_list` | Manage sector maps |
| `/portal/sector-maps/new/` | `sector_map_new` | Upload map |
| `/portal/sector-maps/<slug>/edit/` | `sector_map_edit` | Edit map |
| `/portal/sector-maps/<slug>/delete/` | `sector_map_delete` | Delete map |
| `/portal/leads/` | `site_visit_leads` | Site visit enquiries |
| `/portal/seller-leads/` | `seller_leads` | Seller submissions CRM |

### AJAX Endpoints

| URL | Method | Description |
|---|---|---|
| `/site-visit/` | `POST` | Submit site visit booking |
| `/portal/seller-leads/submit/` | `POST` | Submit seller lead from public form |

---

## Getting Started

**Prerequisites:** Python 3.9+, Node.js 16+

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd realestate

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install and build Tailwind CSS
python manage.py tailwind install
python manage.py tailwind build

# 5. Apply database migrations
python manage.py migrate

# 6. Create the owner account
python manage.py createsuperuser --username concierge

# 7. (Optional) Seed sample listings
python manage.py seed_properties

# 8. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` for the public site and `http://127.0.0.1:8000/portal/` for the owner dashboard.

> **Tailwind watch mode:** Run `python manage.py tailwind start` in a second terminal during development to rebuild CSS on file changes.

---

## Media & Assets

All uploaded media lives under `media/` (excluded from version control).

| Path | Contents |
|---|---|
| `media/properties/primary/` | Primary listing hero images |
| `media/properties/gallery/` | Secondary gallery images |
| `media/properties/suncity heights/` | Suncity Heights listing photos |
| `media/properties/jop palms/` | JOP Palms listing photos |
| `media/properties/farmhouse/` | Luxury Farmhouse listing photos |
| `media/sector_maps/` | Owner-uploaded layout maps |
| `media/office/` | Agency office photos (AVIF format) |
| `media/logo.png` | Source logo file |
| `theme/static/img/logo.png` | Logo copy served as static asset |

---

## Design System

All custom design tokens are defined in `theme/static_src/tailwind.config.js`.

### Colour palette

| Token | Hex | Usage |
|---|---|---|
| `midnight-900` | `#04060f` | Page background |
| `midnight-800` | `#080b1a` | Secondary surfaces |
| `champagne-200` | `#eddfa0` | Headings, highlights |
| `champagne-300` | `#e0c675` | Primary accent, CTAs |
| `champagne-400` | `#d4b158` | Borders, glows |

### Utility classes

| Class | Description |
|---|---|
| `glass` | Frosted-glass surface (backdrop-blur, translucent border) |
| `glass-strong` | Heavier frosted glass for cards and modals |
| `glass-hover` | Glass with hover lift transition |
| `btn-cta` | Champagne-filled primary button with pulse animation |
| `btn-primary` | Solid champagne button |
| `btn-ghost` | Transparent outlined button |
| `form-input` | Glassmorphic text input |
| `form-label` | Uppercase tracked label above inputs |
| `eyebrow` | Small all-caps champagne tracking label |
| `reveal` | Scroll-reveal base class |
| `reveal-up/left/right` | Directional reveal variants |

### Scroll animations

Elements with `.reveal` become `.is-visible` when they enter the viewport via an `IntersectionObserver`. Add `data-delay="150"` (ms) to stagger children.

---

## Portal Credentials

```
URL:       /portal/
Username:  concierge
Password:  mannat@2024
```

To change the password:

```bash
python manage.py changepassword concierge
```

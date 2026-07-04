from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from properties.models import Property, PropertyImage, SectorMap

from .forms import PropertyForm, SectorMapForm, SellerSubmissionForm
from .models import SiteVisitLead, SellerSubmission


class PortalLoginView(LoginView):
    """Branded, glassmorphic sign-in for the client portal."""
    template_name = 'portal/login.html'
    redirect_authenticated_user = True


class PortalLogoutView(LogoutView):
    next_page = reverse_lazy('portal:login')


@login_required(login_url='portal:login')
def dashboard(request):
    """Landing view — headline metrics + a table of listings."""
    qs = Property.objects.all()
    stats = qs.aggregate(total_value=Sum('price'), total=Count('id'))
    leads_qs = SiteVisitLead.objects.all()
    seller_qs = SellerSubmission.objects.all()
    context = {
        'total_properties': stats['total'] or 0,
        'published_count':  qs.filter(is_published=True).count(),
        'draft_count':      qs.filter(is_published=False).count(),
        'total_portfolio_value': stats['total_value'] or 0,
        'recent_properties': qs.order_by('-created_at')[:12],
        'new_leads_count': leads_qs.filter(is_contacted=False).count(),
        'total_leads_count': leads_qs.count(),
        'new_seller_count': seller_qs.filter(status='pending').count(),
        'total_seller_count': seller_qs.count(),
    }
    return render(request, 'portal/dashboard.html', context)


@login_required(login_url='portal:login')
def property_new(request):
    """Create a new listing. Handles multi-file gallery upload."""
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save()
            for idx, image in enumerate(form.cleaned_data.get('gallery_images') or []):
                PropertyImage.objects.create(property=prop, image=image, order=idx)
            messages.success(request, f'"{prop.title}" has been added to the portfolio.')
            return redirect('portal:dashboard')
    else:
        form = PropertyForm()

    return render(request, 'portal/property_form.html', {'form': form, 'mode': 'new'})


@login_required(login_url='portal:login')
def sector_map_list(request):
    """Portal-side list of every SectorMap row + upload / edit shortcuts."""
    return render(request, 'portal/sector_map_list.html', {
        'sector_maps': SectorMap.objects.all(),
    })


@login_required(login_url='portal:login')
def sector_map_new(request):
    """Create + upload a new sector map."""
    if request.method == 'POST':
        form = SectorMapForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'"{obj.name}" has been added to the sector maps gallery.')
            return redirect('portal:sector_map_list')
    else:
        form = SectorMapForm()
    return render(request, 'portal/sector_map_form.html', {'form': form, 'mode': 'new'})


@login_required(login_url='portal:login')
def sector_map_edit(request, slug):
    """Edit / replace an existing sector map's image or metadata."""
    smap = get_object_or_404(SectorMap, slug=slug)
    if request.method == 'POST':
        form = SectorMapForm(request.POST, request.FILES, instance=smap)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'"{obj.name}" has been updated.')
            return redirect('portal:sector_map_list')
    else:
        form = SectorMapForm(instance=smap)
    return render(request, 'portal/sector_map_form.html', {'form': form, 'mode': 'edit', 'sector_map': smap})


@login_required(login_url='portal:login')
def sector_map_delete(request, slug):
    """POST-only delete for a sector map row (guarded by the login decorator)."""
    smap = get_object_or_404(SectorMap, slug=slug)
    if request.method == 'POST':
        name = smap.name
        smap.delete()
        messages.success(request, f'"{name}" has been removed.')
    return redirect('portal:sector_map_list')


@login_required(login_url='portal:login')
def property_edit(request, slug):
    """Edit an existing listing (also supports adding gallery images)."""
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        if form.is_valid():
            prop = form.save()
            existing_count = prop.gallery_images.count()
            for idx, image in enumerate(form.cleaned_data.get('gallery_images') or []):
                PropertyImage.objects.create(
                    property=prop, image=image, order=existing_count + idx,
                )
            messages.success(request, f'"{prop.title}" has been updated.')
            return redirect('portal:dashboard')
    else:
        form = PropertyForm(instance=prop)

    return render(request, 'portal/property_form.html', {'form': form, 'mode': 'edit', 'property': prop})


@login_required(login_url='portal:login')
def property_delete(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        title = prop.title
        prop.delete()
        messages.success(request, f'"{title}" has been removed from the portfolio.')
    return redirect('portal:dashboard')


@login_required(login_url='portal:login')
def seller_leads(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('status')
        if lead_id and new_status:
            lead = get_object_or_404(SellerSubmission, id=lead_id)
            lead.status = new_status
            lead.save()
        return redirect('portal:seller_leads')
    leads = SellerSubmission.objects.all()
    context = {
        'leads': leads,
        'new_count': leads.filter(status='pending').count(),
        'total_count': leads.count(),
    }
    return render(request, 'portal/seller_leads.html', context)


@require_POST
def submit_seller(request):
    form = SellerSubmissionForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@require_POST
def submit_site_visit(request):
    """Public endpoint — receive a site visit enquiry and store it as a lead."""
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    preferred_location = request.POST.get('preferred_location', '').strip()
    property_ref = request.POST.get('property_ref', '').strip()

    if not name or not phone or not preferred_location:
        return JsonResponse({'ok': False, 'error': 'Please fill in all required fields.'}, status=400)

    SiteVisitLead.objects.create(
        name=name,
        phone=phone,
        preferred_location=preferred_location,
        property_ref=property_ref,
    )
    return JsonResponse({'ok': True})


@login_required(login_url='portal:login')
def site_visit_leads(request):
    """Portal dashboard — list of incoming site visit enquiries."""
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        if lead_id:
            lead = get_object_or_404(SiteVisitLead, id=lead_id)
            lead.is_contacted = not lead.is_contacted
            lead.save()
        return redirect('portal:site_visit_leads')

    leads = SiteVisitLead.objects.all()
    context = {
        'leads': leads,
        'new_count': leads.filter(is_contacted=False).count(),
        'total_count': leads.count(),
    }
    return render(request, 'portal/leads.html', context)

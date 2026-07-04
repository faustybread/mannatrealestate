from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.PortalLoginView.as_view(), name='login'),
    path('logout/', views.PortalLogoutView.as_view(), name='logout'),
    path('properties/new/', views.property_new, name='property_new'),
    path('properties/<slug:slug>/edit/', views.property_edit, name='property_edit'),
    path('sector-maps/', views.sector_map_list, name='sector_map_list'),
    path('sector-maps/new/', views.sector_map_new, name='sector_map_new'),
    path('sector-maps/<slug:slug>/edit/', views.sector_map_edit, name='sector_map_edit'),
    path('sector-maps/<slug:slug>/delete/', views.sector_map_delete, name='sector_map_delete'),
    path('leads/', views.site_visit_leads, name='site_visit_leads'),
    path('leads/submit/', views.submit_site_visit, name='submit_site_visit'),
    path('properties/<slug:slug>/delete/', views.property_delete, name='property_delete'),
    path('seller-leads/', views.seller_leads, name='seller_leads'),
    path('seller-leads/submit/', views.submit_seller, name='submit_seller'),
]

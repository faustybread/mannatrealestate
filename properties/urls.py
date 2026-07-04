from django.urls import path

from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.homepage, name='home'),
    path('properties/', views.property_list, name='list'),
    path('properties/<slug:slug>/', views.property_detail, name='detail'),
    path('sitemaps/', views.sector_maps, name='sector_maps'),
    path('about/', views.about, name='about'),
    path('site-visit/', views.site_visit_page, name='site_visit'),
    path('list-property/', views.list_property_page, name='list_property'),
    path('projects/omaxe-city/', views.omaxe_city_plot_layout, name='omaxe_city_plots'),
]

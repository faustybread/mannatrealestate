from django.contrib import admin

from .models import Property, PropertyImage, SectorMap


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'bedrooms', 'bathrooms', 'is_published', 'created_at')
    list_filter = ('is_published', 'bedrooms', 'bathrooms')
    search_fields = ('title', 'location', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'primary_image', 'is_published'),
        }),
        ('Pricing & specs', {
            'fields': ('price', 'bedrooms', 'bathrooms', 'square_footage', 'features_list'),
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude'),
            'description': 'Latitude/longitude power the Google Maps embed on the property detail page.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'order')


@admin.register(SectorMap)
class SectorMapAdmin(admin.ModelAdmin):
    """Upload / manage official township & sector layout maps."""
    list_display = ('name', 'order', 'is_published', 'has_image', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(boolean=True, description='Image uploaded')
    def has_image(self, obj):
        return bool(obj.image)

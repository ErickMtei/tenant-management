from django.contrib import admin

from .models import Lease, Payment, Property, Tenant, Unit


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'created_at')
    search_fields = ('name', 'address', 'city')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'property', 'monthly_rent', 'status')
    list_filter = ('status', 'property')
    search_fields = ('unit_number', 'property__name')
    list_select_related = ('property',)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'email', 'national_id')
    search_fields = ('full_name', 'phone_number', 'national_id')


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'unit', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = (
        'tenant__full_name',
        'tenant__phone_number',
        'unit__unit_number',
        'unit__property__name',
    )
    autocomplete_fields = ('tenant', 'unit')
    list_select_related = ('tenant', 'unit__property')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('lease', 'amount', 'payment_date', 'period_month', 'method')
    list_filter = ('method',)
    date_hierarchy = 'payment_date'
    autocomplete_fields = ('lease',)
    search_fields = ('lease__tenant__full_name', 'reference')
    list_select_related = ('lease__tenant', 'lease__unit__property')
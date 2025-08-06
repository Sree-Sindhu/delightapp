from django.contrib import admin
from .models import Cake, Store, CartItem, CustomerProfile, DeliveryAgent

admin.site.register(Cake)
admin.site.register(Store)
admin.site.register(CartItem)

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender')
    search_fields = ('user__username', 'phone_number')

admin.site.register(CustomerProfile, CustomerProfileAdmin)

@admin.register(DeliveryAgent)
class DeliveryAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'is_available', 'location')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_available',)
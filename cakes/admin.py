from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Cake, Store, CartItem, CustomerProfile, DeliveryAgent, 
    Order, OrderItem, OrderStatusHistory, OrderAlert,
    Address, Category, Review, StoreReview
)

# Enhanced admin for better order management
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_display', 'status_display', 'total_items', 
        'created_at', 'estimated_delivery_time', 'agent_display'
    )
    list_filter = ('status', 'created_at', 'estimated_delivery_time')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('id', 'created_at', 'last_updated', 'order_history_display')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'created_at', 'last_updated')
        }),
        ('Order Status', {
            'fields': ('status', 'agent', 'estimated_delivery_time'),
            'classes': ('wide',)
        }),
        ('History', {
            'fields': ('order_history_display',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_out_for_delivery', 'mark_delivered', 'mark_cancelled']
    
    def user_display(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    user_display.short_description = "Customer"
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffa500',
            'confirmed': '#007bff',
            'preparing': '#6610f2',
            'ready': '#20c997',
            'out_for_delivery': '#17a2b8',
            'delivered': '#28a745',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"
    
    def total_items(self, obj):
        return obj.items.count()
    total_items.short_description = "Items"
    
    def agent_display(self, obj):
        if obj.agent:
            return f"{obj.agent.name} ({obj.agent.phone})"
        return "-"
    agent_display.short_description = "Delivery Agent"
    
    def order_history_display(self, obj):
        history = obj.status_history.all().order_by('-timestamp')
        if not history:
            return "No history available"
        
        html = "<table style='width: 100%;'>"
        html += "<tr><th>Status</th><th>Timestamp</th></tr>"
        for h in history:
            html += f"<tr><td>{h.status}</td><td>{h.timestamp}</td></tr>"
        html += "</table>"
        return mark_safe(html)
    order_history_display.short_description = "Status History"
    
    # Custom actions
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_preparing(self, request, queryset):
        updated = queryset.update(status='preparing')
        self.message_user(request, f'{updated} orders marked as Preparing.')
    mark_preparing.short_description = "Mark selected orders as Preparing"
    
    def mark_ready(self, request, queryset):
        updated = queryset.update(status='ready')
        self.message_user(request, f'{updated} orders marked as Ready for Pickup.')
    mark_ready.short_description = "Mark selected orders as Ready for Pickup"
    
    def mark_out_for_delivery(self, request, queryset):
        updated = queryset.update(status='out_for_delivery')
        self.message_user(request, f'{updated} orders marked as Out for Delivery.')
    mark_out_for_delivery.short_description = "Mark selected orders as Out for Delivery"
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as Delivered.')
    mark_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as Cancelled.')
    mark_cancelled.short_description = "Mark selected orders as Cancelled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'cake', 'quantity', 'unit_price', 'total_price')
    list_filter = ('cake', 'order__status')
    search_fields = ('order__id', 'cake__name')
    
    def order_id(self, obj):
        return obj.order.id
    order_id.short_description = "Order ID"
    
    def total_price(self, obj):
        return obj.quantity * obj.unit_price
    total_price.short_description = "Total Price"

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__id',)
    readonly_fields = ('timestamp',)

@admin.register(DeliveryAgent)
class DeliveryAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'availability_status', 'current_orders', 'location')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('is_available',)
    
    def availability_status(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✅ Available</span>')
        else:
            return format_html('<span style="color: red;">❌ Busy</span>')
    availability_status.short_description = "Status"
    
    def current_orders(self, obj):
        active_orders = Order.objects.filter(
            agent=obj, 
            status__in=['confirmed', 'out_for_delivery']
        ).count()
        return active_orders
    current_orders.short_description = "Active Orders"

# Enhanced admin for other models
@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'flavor', 'size', 'category', 'price', 'store_count')
    list_filter = ('category', 'flavor', 'size')
    search_fields = ('name', 'flavor')
    filter_horizontal = ('stores',)
    
    def store_count(self, obj):
        return obj.stores.count()
    store_count.short_description = "Available Stores"

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone_number', 'cake_count', 'coordinates')
    search_fields = ('name', 'location')
    
    def cake_count(self, obj):
        return obj.cakes.count()
    cake_count.short_description = "Available Cakes"
    
    def coordinates(self, obj):
        return f"{obj.latitude}, {obj.longitude}"
    coordinates.short_description = "Lat, Lng"

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'total_orders')
    search_fields = ('user__username', 'phone_number')
    
    def total_orders(self, obj):
        return Order.objects.filter(user=obj.user).count()
    total_orders.short_description = "Total Orders"

# Register other models with simple admin
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(StoreReview)
admin.site.register(OrderAlert)

# Customize admin site headers
admin.site.site_header = "DelightAPI Administration"
admin.site.site_title = "DelightAPI Admin"
admin.site.index_title = "Welcome to DelightAPI Administration"
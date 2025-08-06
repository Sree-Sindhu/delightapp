from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CakeViewSet, StoreViewSet, CartViewSet, OrderViewSet, AddressViewSet,
    DeliveryAgentViewSet, CustomerSignupView, LoginView, LogoutView,
    CustomerProfileView, UserView, DeleteAccountView, ChangePasswordView,
    sales_analytics, top_selling_cakes, UpdateAgentLocationView,
    ReviewViewSet, CategoryViewSet
)
from django.http import HttpResponse

# A router automatically handles URL patterns for ViewSets
# This creates URLs like:
# /cakes/, /cakes/{pk}/
# /stores/, /stores/{pk}/
# /orders/, /orders/{pk}/, /orders/{pk}/cancel/, etc.
# /addresses/, /addresses/{pk}/
router = DefaultRouter()
router.register(r'cakes', CakeViewSet, basename='cake')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'agents', DeliveryAgentViewSet, basename='agent')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'categories', CategoryViewSet, basename='category')

# A simple home view for the root URL
def index(request):
    return HttpResponse("<h1>Welcome to DelightAPI Backend!</h1><p>API endpoints are under /api/</p>")

urlpatterns = [
    path('', index, name='home'),
    
    # All API endpoints are now under a single '/api/' prefix for clarity
    path('api/', include(router.urls)),
    
    # --- Authentication & Profile URLs (APIViews, not ViewSets) ---
    path('auth/register/', CustomerSignupView.as_view(), name='customer-signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserView.as_view(), name='user'),
    path('auth/profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('auth/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # --- Analytics URLs (@api_view function-based views) ---
    path('analytics/sales/', sales_analytics, name='sales-analytics'),
    path('analytics/top-cakes/', top_selling_cakes, name='top-cakes'),

    # --- Specific Agent Action ---
    path('agents/<int:agent_id>/location-update/', UpdateAgentLocationView.as_view(), name='agent-location-update'),
]
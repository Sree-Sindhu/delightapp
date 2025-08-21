from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CakeViewSet, StoreViewSet, CartViewSet, OrderViewSet, AddressViewSet,
    DeliveryAgentViewSet, CustomerSignupView, LoginView, LogoutView,
    CustomerProfileView, UserView, DeleteAccountView, ChangePasswordView,
    sales_analytics, top_selling_cakes, UpdateAgentLocationView,
    ReviewViewSet, CategoryViewSet, StoreReviewViewSet, PasswordResetView
)
from django.http import HttpResponse

# A router automatically handles URL patterns for ViewSets
router = DefaultRouter()
router.register(r'cakes', CakeViewSet, basename='cake')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'agents', DeliveryAgentViewSet, basename='agent')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'store-reviews', StoreReviewViewSet, basename='store-review')

urlpatterns = [
    path('', include(router.urls)), # Router URLs (e.g. /cakes/, /stores/)
    
    # Authentication & Profile URLs
    path('auth/register/', CustomerSignupView.as_view(), name='customer-signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/user/', UserView.as_view(), name='user'),
    path('auth/profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('auth/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password-reset'),

    # Analytics URLs
    path('analytics/sales/', sales_analytics, name='sales-analytics'),
    path('analytics/top-cakes/', top_selling_cakes, name='top-cakes'),

    # Specific Agent Action
    path('agents/<int:agent_id>/location-update/', UpdateAgentLocationView.as_view(), name='agent-location-update'),
]
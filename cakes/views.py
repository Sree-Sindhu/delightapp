from django.contrib.auth.models import User
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Sin, Cos, Radians, Power, ASin, Sqrt
from rest_framework.decorators import api_view, permission_classes, action
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import (
    Cake, Store, CartItem, Order, OrderItem, OrderStatusHistory, OrderAlert,
    DeliveryAgent, CustomerProfile, Address, Review, Category
)
from .serializers import (
    CakeSerializer, StoreSerializer, CartItemSerializer, OrderItemSerializer,
    OrderSerializer, OrderTrackingSerializer, OrderStatusHistorySerializer,
    OrderAlertSerializer, AgentSerializer, DeliveryAgentLocationSerializer,
    UserRegistrationSerializer, CustomerProfileSerializer, AddressSerializer,
    ReviewSerializer, CategorySerializer
)


# --- AUTHENTICATION & USER PROFILE VIEWS ---
class CustomerSignupView(generics.CreateAPIView):
    """
    Registers a new user with nested address and profile data.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    """
    Handles user login and returns an auth token.
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)

class LogoutView(APIView):
    """
    Logs out the authenticated user by deleting their auth token.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})

class UserView(APIView):
    """
    Retrieves the basic details of the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
        
class DeleteAccountView(APIView):
    """
    Deletes the authenticated user's account.
    """
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class ChangePasswordView(APIView):
    """
    Allows an authenticated user to change their password.
    """
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not user.check_password(current_password):
            return Response({"error": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})

class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """
    Allows authenticated users to view and update their profile.
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        profile, created = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile


# --- CAKE, STORE, & ADDRESS VIEWS ---
class CakeViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing cakes.
    """
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        cake = self.get_object()
        reviews = cake.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the user to the authenticated user
        serializer.save(user=self.request.user)
    
    # You can add a custom list method to filter by cake
    def get_queryset(self):
        queryset = super().get_queryset()
        cake_id = self.request.query_params.get('cake_id')
        if cake_id:
            queryset = queryset.filter(cake_id=cake_id)
        return queryset
    
class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for listing or retrieving stores.
    Supports distance-based sorting if 'lat' and 'lon' query params are provided.
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_lat = self.request.query_params.get('lat')
        user_lon = self.request.query_params.get('lon')
        if user_lat and user_lon:
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                earth_radius_km = 6371
                queryset = queryset.annotate(
                    distance=ExpressionWrapper(
                        earth_radius_km * 2 * ASin(Sqrt(
                            Power(Sin((Radians(F('latitude')) - Radians(user_lat)) / 2), 2) +
                            Cos(Radians(user_lat)) * Cos(Radians(F('latitude'))) *
                            Power(Sin((Radians(F('longitude')) - Radians(user_lon)) / 2), 2)
                        )),
                        output_field=FloatField()
                    )
                ).order_by('distance')
            except (ValueError, TypeError):
                pass
        return queryset

    @action(detail=True, methods=['get'])
    def cakes(self, request, pk=None):
        store = self.get_object()
        cakes_queryset = store.cakes.all()
        serializer = CakeSerializer(cakes_queryset, many=True)
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for users to manage their multiple addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        return self.request.user.addresses.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing cake categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Or whatever permissions you need

# --- CART & ORDER VIEWS ---
class CartViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for a user's cart. Handles listing, adding, updating, and removing items.
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Handles order CRUD operations for users and provides admin access.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if obj.user != user and not user.is_staff:
            raise PermissionDenied("You don't have access to this order.")
        return obj
    
    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'confirmed']:
            return Response({"detail": "This order cannot be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        if order.status == 'cancelled':
            return Response({"detail": "Order is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        serializer = OrderSerializer(order, data={'status': new_status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        order = self.get_object()
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        order = self.get_object()
        history = order.status_history.order_by('timestamp')
        serializer = OrderStatusHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        order = self.get_object()
        alerts = order.alerts.order_by('-timestamp')
        serializer = OrderAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def agent(self, request, pk=None):
        order = self.get_object()
        if not order.agent:
            return Response({'detail': 'No delivery agent assigned yet'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AgentSerializer(order.agent)
        return Response(serializer.data)


# --- DELIVERY AGENT VIEWS ---
class DeliveryAgentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for viewing delivery agents.
    """
    queryset = DeliveryAgent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], url_path='available')
    def available_agents(self, request):
        agents = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(agents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        agent = self.get_object()
        serializer = DeliveryAgentLocationSerializer(agent)
        return Response(serializer.data)

class UpdateAgentLocationView(APIView):
    """
    Updates a delivery agent's location and sends a WebSocket message.
    """
    permission_classes = [IsAdminUser]
    def post(self, request, agent_id):
        try:
            agent = DeliveryAgent.objects.get(id=agent_id)
        except DeliveryAgent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)
        location = request.data.get("location")
        agent.location = location
        agent.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'agent_{agent_id}',
            {
                'type': 'send_location_update',
                'data': {
                    'location': location,
                    'agent_id': agent_id
                }
            }
        )
        return Response({"message": "Location updated successfully"})


# --- ANALYTICS VIEWS ---
@api_view(['GET'])
@permission_classes([IsAdminUser])
def sales_analytics(request):
    total_sales = OrderItem.objects.aggregate(total=Sum(F('quantity') * F('cake__price'), output_field=FloatField()))['total'] or 0
    total_orders = Order.objects.count()
    return Response({"total_sales": total_sales, "total_orders": total_orders})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def top_selling_cakes(request):
    top_cakes = (OrderItem.objects
                 .values('cake__id', 'cake__name')
                 .annotate(sold=Sum('quantity'))
                 .order_by('-sold')[:5])
    return Response(top_cakes)
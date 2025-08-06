# serializers.py
from rest_framework import serializers
from .models import Cake, Store, CartItem, Order, OrderItem, OrderStatusHistory, OrderAlert, DeliveryAgent, CustomerProfile, Address, Review
from django.contrib.auth.models import User

class CakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cake
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = Cake
        fields = ['id', 'name', 'flavor', 'size', 'price', 'category_name', 'category']
        read_only_fields = ['category_name']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'cake', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class StoreSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False)
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'phone_number', 'distance']
        
class CartItemSerializer(serializers.ModelSerializer):
    cake_name = serializers.ReadOnlyField(source='cake.name')

    class Meta:
        model = CartItem
        fields = ['id', 'cake', 'cake_name', 'quantity', 'customization', 'added_at']

class OrderItemSerializer(serializers.ModelSerializer):
    cake_name = serializers.CharField(source='cake.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'cake', 'cake_name', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'created_at',
            'status',
            'estimated_delivery_time',
            'agent',
            'items',
        ]
        read_only_fields = ['user', 'created_at', 'items']

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status', 'estimated_delivery_time', 'last_updated']

class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['status', 'timestamp']

class OrderAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAlert
        fields = ['alert_type', 'message', 'timestamp']

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAgent
        fields = ['id', 'name', 'phone', 'email']

class DeliveryAgentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAgent
        fields = ['id', 'name', 'location', 'is_available']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'flat_number', 'building_name', 'street', 'area_or_colony',
            'landmark', 'city', 'state', 'pincode', 'latitude', 'longitude'
        ]
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=CustomerProfile.GENDER_CHOICES, write_only=True)
    address = AddressSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'phone_number', 'gender', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phone_number')
        gender = validated_data.pop('gender')
        address_data = validated_data.pop('address')
    
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        Address.objects.create(user=user, **address_data)

        # Create profile
        CustomerProfile.objects.create(
            user=user,
            phone_number=phone,
            gender=gender
        )

        return user
    
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'gender']
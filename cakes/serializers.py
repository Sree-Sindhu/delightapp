# serializers.py
from rest_framework import serializers
from .models import Cake, Store, CartItem, Order, OrderItem, OrderStatusHistory, OrderAlert, DeliveryAgent, CustomerProfile, Address, Review, StoreReview
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
        

        

# New serializer for store reviews
class StoreReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = StoreReview
        fields = ['id', 'user', 'store', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


# Update the existing StoreSerializer to show the average rating
class StoreSerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False)
    # Add a new field to display the average rating
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'phone_number', 'distance', 'average_rating']

class CartItemSerializer(serializers.ModelSerializer):
    cake_name = serializers.ReadOnlyField(source='cake.name')

    class Meta:
        model = CartItem
        fields = ['id', 'cake', 'cake_name', 'quantity', 'customization', 'added_at']

class OrderItemSerializer(serializers.ModelSerializer):
    cake_name = serializers.CharField(source='cake.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'cake', 'cake_name', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

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
            'total_amount',
        ]
        read_only_fields = ['user', 'created_at', 'items']

    def get_total_amount(self, obj: Order):
        from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
        total = Decimal('0.00')
        for it in obj.items.select_related('cake').all():
            try:
                # Prefer unit_price when present and > 0, else fall back to cake.price
                up = it.unit_price
                if up is not None:
                    try:
                        up_dec = Decimal(up)
                    except (InvalidOperation, TypeError):
                        up_dec = Decimal('0.00')
                else:
                    up_dec = Decimal('0.00')
                if up_dec <= 0:
                    try:
                        up_dec = Decimal(it.cake.price)
                    except (InvalidOperation, TypeError):
                        up_dec = Decimal('0.00')
                qty = int(it.quantity or 1)
                total += (up_dec * qty)
            except Exception:
                # Skip problematic items instead of zeroing the whole order
                continue
        # Quantize to 2 decimals and return as float for JSON
        return float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

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
    read_only_fields = ['id', 'latitude', 'longitude']
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=CustomerProfile.GENDER_CHOICES, write_only=True)
    address = AddressSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'phone_number', 'gender', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        phone = validated_data.pop('phone_number', None)
        gender = validated_data.pop('gender', None)

        # Create user (The signal will automatically create the profile for you)
        user = User.objects.create_user(**validated_data)
        
        # Now, create the Address and update the profile with phone and gender
        if address_data:
            Address.objects.create(user=user, **address_data)

        # Update the newly created profile with phone_number and gender
        user.profile.phone_number = phone
        user.profile.gender = gender
        user.profile.save()

        return user
    
class CustomerProfileSerializer(serializers.ModelSerializer):
    # Dotted-source fields for the User model (first_name, last_name)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)

    # Nested serializer for the Address model
    # Set many=False as each CustomerProfile has one Address
    address = AddressSerializer(required=False) 

    class Meta:
        model = CustomerProfile
        fields = [
            'phone_number', 'gender', 'first_name', 'last_name', 'address'
        ]

    def update(self, instance, validated_data):
        # 1. Handle User model fields (first_name, last_name)
        user_data = validated_data.pop('user', {})
        user = instance.user # Get the related User instance

        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.save()

        # 2. Handle nested Address data
        address_data = validated_data.pop('address', {})
        
        # Get or create the Address instance linked to this CustomerProfile
        # Assuming Address model has a OneToOneField or ForeignKey to CustomerProfile
        # If Address is directly linked to User, you might need user.address_set.first() or similar.
        # Based on UserRegistrationSerializer, it's linked to User.
        # Let's adjust to get_or_create from the User, assuming it's a OneToOne or similar.
        # If Address.user is a OneToOneField:
        address_instance, created = Address.objects.get_or_create(user=user)
        
        for attr, value in address_data.items():
            # Only update fields that are actually in the Address model and not read-only
            if attr not in self.fields['address'].read_only_fields:
                setattr(address_instance, attr, value)
        address_instance.save()

        # 3. Handle CustomerProfile's own fields (phone_number, gender)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()

        return instance
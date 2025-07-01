from unicodedata import category
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from organization.models import EndDayDailyReport
from product.models import CustomerProduct, Product, ProductCategory,ProductMultiprice, BranchStockTracking, ItemReconcilationApiItem, BranchStock


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "title", "slug", "description"]



class ProductSerializer(ModelSerializer):
    # category = ProductCategorySerializer()
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()

    ledger_name = serializers.SerializerMethodField()
    # stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "price",
            "is_taxable",
            "product_id",
            "unit",
            "category",
            "barcode",
            'reconcile',
            'is_billing_item',
            'ledger',
            'ledger_name',
            'opening_count',
            'is_produced',
            'cost_price',
            'discount_exempt',
            # 'stock_quantity',
            'minimum_stock',
            "excise_duty_applicable",
            "importtax_percent"

        ]
    def get_ledger_name(self, obj):
        # Check if the ledger field is not None
            if obj.ledger:
                return obj.ledger.ledger_name
            else:
                return None  # Return None if ledger is None
    
    def get_category(self, obj):
        return obj.category.title
        
    def get_price(self, obj):
        return float(obj.price)
        
    def get_cost_price(self, obj):
        return float(obj.cost_price) 
        
    # def get_stock_quantity(self, obj):
    #     branch = self.context.get("branch")
    #     # print(branch)
    #     if branch:
    #         branchstock_data = BranchStock.objects.filter(product=obj, branch__id=int(branch)).values('quantity')
    #         total_quantity = sum(entry['quantity'] for entry in branchstock_data)
    #         return total_quantity
    #     return 0
        
class ProductSerializerList(ModelSerializer):
    # category = ProductCategorySerializer()
    category = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()

    ledger_name = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "price",
            "is_taxable",
            "product_id",
            "unit",
            "category",
            "barcode",
            'reconcile',
            'is_billing_item',
            'ledger',
            'ledger_name',
            'opening_count',
            'is_produced',
            'cost_price',
            'discount_exempt',
            'stock_quantity',
            'minimum_stock'

        ]
    def get_ledger_name(self, obj):
        # Check if the ledger field is not None
            if obj.ledger:
                return obj.ledger.ledger_name
            else:
                return None  # Return None if ledger is None
    
    def get_category(self, obj):
        return obj.category.title
        
    def get_price(self, obj):
        return float(obj.price)
        
    def get_cost_price(self, obj):
        return float(obj.cost_price) 
        
    def get_stock_quantity(self, obj):
        branch = self.context.get("branch")
        # print(branch)
        if branch:
            branchstock_data = BranchStock.objects.filter(product=obj, branch__id=int(branch)).values('quantity')
            total_quantity = sum(entry['quantity'] for entry in branchstock_data)
            return int(total_quantity)
        return 0


class CustomerProductSerializer(ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = [
            "product",
            "customer",
            "price",
        ]


class PriceLessProductSerializer(ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "image",
            "is_taxable",
            "product_id",
            "unit",
            "category",
        ]


class CustomerProductDetailSerializer(ModelSerializer):
    product = PriceLessProductSerializer()
    agent = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = CustomerProduct
        fields = [
            "product",
            "price",
            "customer",
            "agent",
        ]

        optional_fields = ["agent"]

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        product_representation = representation.pop("product")
        for key in product_representation:
            representation[key] = product_representation[key]

        return representation

    def to_internal_value(self, data):
        product_internal = {}
        for key in PriceLessProductSerializer.Meta.fields:
            if key in data:
                product_internal[key] = data.pop(key)
        internal = super().to_internal_value(data)
        internal["product"] = product_internal
        return internal


class BranchStockTrackingSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    class Meta:
        model = BranchStockTracking
        fields = "branch", "product", 'wastage', 'returned', 'physical', 'date'


class ProductReconcileSerializer(serializers.Serializer):
    products = BranchStockTrackingSerializer(many=True)


class EndDayDailyReportSerializer(ModelSerializer):
    class Meta:
        model = EndDayDailyReport
        exclude = [
            'created_at', 'updated_at', 'status', 'is_deleted', 'sorting_order', 'is_featured'
        ]


class ItemReconcilationApiItemSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=True)
    class Meta:
        model = ItemReconcilationApiItem
        fields = 'branch', 'product', 'date', 'wastage', 'returned', 'physical'


from organization.models import Terminal
class BulkItemReconcilationApiItemSerializer(serializers.Serializer):
    items = ItemReconcilationApiItemSerializer(many=True)
    terminal = serializers.CharField(max_length=20, required=True)
    branch = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    report_total = EndDayDailyReportSerializer()
    
    def create(self, validated_data):
        items = validated_data.get('items', [])
        terminal = validated_data.get('terminal') 
        branch = validated_data.get('branch') 
        for item in items:
            item['terminal'] = Terminal.objects.get(branch__id=branch, terminal_no=int(terminal))
            ItemReconcilationApiItem.objects.create(**item)
        return validated_data
        
        
class ProductSerializerCreate(ModelSerializer):
    class Meta:
        model=Product
        exclude = [
            "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured",
            "slug"
        ]
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

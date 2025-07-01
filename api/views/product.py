from django.forms import ValidationError
from rest_framework.response import Response
from api.serializers.product import (
    CustomerProductDetailSerializer,
    CustomerProductSerializer,
    ProductSerializer,
    BulkItemReconcilationApiItemSerializer,
    ProductSerializerCreate,
    ProductSerializerList,

)
from rest_framework.views import APIView

from rest_framework.generics import ListAPIView, RetrieveAPIView

from product.models import CustomerProduct, Product,ProductMultiprice, BranchStock, ItemReconcilationApiItem, RequisitionBranchStock
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json
from django.shortcuts import get_object_or_404
from organization.models import Branch, Organization

import jwt
from django.db.models import OuterRef, Subquery, Sum

class ProductMultipriceapi(ListAPIView):
    def get(self, request):
        try:
            products_list = Product.objects.all().values(
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
        "barcode"
        )
            temp_data = products_list
            for index,item in enumerate(products_list):
                print(item["id"])
                queryset = ProductMultiprice.objects.filter(product_id=item["id"]).values()
                temp_data[index]["multiprice"]=queryset
            return Response(temp_data,200)

        except Exception as error:
            return Response({"message":str(error)})






# class ProductList(ListAPIView):
#     serializer_class = ProductSerializer
#     pagination_class = None

#     def get_queryset(self):
#         return Product.objects.active()

from rest_framework import viewsets

class ProductList(viewsets.ViewSet):
    # serializer_class = ProductSerializer
    # pagination_class = None

    # def get_queryset(self):
    #     return Product.objects.active()
    
    def list(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        jwt_token = jwt_token.split()[1]
        try:
            token_data = jwt.decode(jwt_token, options={"verify_signature": False})  # Disable signature verification for claims extraction
            user_id = token_data.get("user_id")
            username = token_data.get("username")
            role = token_data.get("role")
            # You can access other claims as needed 

            # Assuming "branch" is one of the claims, access it
            branch = token_data.get("branch")

            # Print the branch
            print("Branch:", branch)
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.DecodeError:
            print("Token is invalid.")

        branchstock_quantity_subquery_all = BranchStock.objects.filter(
            product=OuterRef('pk'),
            branch=branch
        ).values('product').annotate(total_quantity=Sum('quantity')).values('total_quantity')[:1]
        org = Organization.objects.first()
        
        if org.allow_negative_sales == True: 
            all_products = Product.objects.filter(
                is_deleted = False,
                is_billing_item=True
            )
        else:
            all_products = Product.objects.annotate(branchstock_total_quantity=Subquery(branchstock_quantity_subquery_all)).filter(
                is_deleted = False,
                branchstock_total_quantity__gt=0
            )
        all_products_serializer = ProductSerializerList(all_products, many=True, context={"branch": branch})

        return Response(all_products_serializer.data)
        
class ProductWithBranchStockList(viewsets.ViewSet):
    # serializer_class = ProductSerializer
    # pagination_class = None

    # def get_queryset(self):
    #     return Product.objects.active()
    
    def list(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        jwt_token = jwt_token.split()[1]
        try:
            token_data = jwt.decode(jwt_token, options={"verify_signature": False})  # Disable signature verification for claims extraction
            user_id = token_data.get("user_id")
            username = token_data.get("username")
            role = token_data.get("role")
            # You can access other claims as needed 

            # Assuming "branch" is one of the claims, access it
            branch = token_data.get("branch")

            # Print the branch
            print("Branch:", branch)
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
        except jwt.DecodeError:
            print("Token is invalid.")

        branchstock_quantity_subquery_all = BranchStock.objects.filter(
            product=OuterRef('pk'),
            branch=branch
        ).values('product').annotate(total_quantity=Sum('quantity')).values('total_quantity')[:1]

        # all_products = Product.objects.filter(
        #     is_deleted = False,
        #     is_billing_item=True
        # )
        # all_products = Product.objects.annotate(branchstock_total_quantity=Subquery(branchstock_quantity_subquery_all)).filter(
        #     is_deleted = False,
        #     branchstock_total_quantity__gt=0
        # )
        all_products = Product.objects.filter(
                is_deleted = False,
                is_billing_item=True
            )
        all_products_serializer = ProductSerializerList(all_products, many=True, context={"branch": branch})

        return Response(all_products_serializer.data)


class ProductDetail(RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Product.objects.active()
        
    # def get_serializer_context(self):
    #     # Get the default context first
    #     context = super().get_serializer_context()
        
    #     jwt_token = self.request.META.get("HTTP_AUTHORIZATION")
    #     jwt_token = jwt_token.split()[1]
    #     try:
    #         token_data = jwt.decode(jwt_token, options={"verify_signature": False})  # Disable signature verification for claims extraction
    #         user_id = token_data.get("user_id")
    #         username = token_data.get("username")
    #         role = token_data.get("role")
    #         # You can access other claims as needed 

    #         # Assuming "branch" is one of the claims, access it
    #         branch = token_data.get("branch")
    #     except jwt.ExpiredSignatureError:
    #         print("Token has expired.")
    #     except jwt.DecodeError:
    #         print("Token is invalid.")
    #     # Add 'branch' to the context dictionary
    #     context['branch'] = branch # Example: Fetch 'branch' from query parameter

    #     return context


class CustomerProductAPI(ModelViewSet):
    serializer_class = CustomerProductSerializer
    queryset = CustomerProduct.objects.active()

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        is_added = CustomerProduct.objects.filter(
            is_deleted=False,
            status=True,
            customer=request.data["customer"],
            product=request.data["product"],
        )

        if not is_added:
            return super().create(request, *args, **kwargs)
        else:
            return Response(
                {"message": "This product is already added to the customer"},
            )

    def get_queryset(self, *args, **kwargs):
        customer_id = self.request.query_params.get("customerId")
        if customer_id:
            queryset = CustomerProduct.objects.filter(
                is_deleted=False, status=True, customer=customer_id
            )

            return queryset
        else:
            return super().get_queryset()

    def get_serializer_class(self):
        detail_actions = ["retrieve", "list"]
        if self.action in detail_actions:
            return CustomerProductDetailSerializer
        return super().get_serializer_class()


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_product_requisition(request):
    data = request.data.get('data', None)
    if data:
        data = json.loads(data)
        for d in data:
            quantity = int(d['quantity'])
            BranchStock.objects.create(branch_id=d['branch_id'], product_id=d['product_id'], quantity=quantity)
            RequisitionBranchStock.objects.create(branch_id=d['branch_id'], product_id=d['product_id'], quantity=quantity)
        return Response({'detail':'ok'}, 201)
    return Response({'detail':'Invalid data'}, 400)



from organization.models import EndDayRecord, EndDayDailyReport
from bill.models import Bill
from datetime import date
class ApiItemReconcilationView(APIView):

    def post(self, request):
        serializer = BulkItemReconcilationApiItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        EndDayRecord.objects.create(branch_id = serializer.validated_data.get('branch'),
                                     terminal=serializer.validated_data.get('terminal'),
                                     date = serializer.validated_data.get('date')
                                     )
        report_total = serializer.validated_data.get("report_total")
        new_data = {'branch_id':serializer.validated_data.get('branch'),'terminal':serializer.validated_data.get('terminal'), **report_total}
        EndDayDailyReport.objects.create(**new_data)
        Bill.objects.filter(branch=serializer.validated_data.get('branch'), terminal=serializer.validated_data.get('terminal'), is_end_day=False).update(is_end_day=True)
        return Response({'details':'success'}, 201)
    
from organization.models import Terminal
class CheckAllowReconcilationView(APIView):

    def get(self, request):
        today_date = date.today()
        branch_id = request.GET.get('branch_id', None)
        terminal = request.GET.get('terminal', None)

        print(f"terminal {terminal}")
        if not branch_id:
            return Response({'detail':'Please provide branch_id in url params'}, 400)
        if not terminal:
            return Response({'detail':'Please provide terminal in url params'}, 400)
        

        branch = get_object_or_404(Branch, pk=branch_id)

        # terminal_obj = get_object_or_404(Terminal, branch=branch, terminal_no=terminal)
        terminal_obj = Terminal.objects.get(branch=branch, terminal_no=terminal)
        print(f"terminal_obj {terminal_obj}")
        if ItemReconcilationApiItem.objects.filter(date=today_date, branch = branch, terminal=terminal_obj).exists():
            return Response({'detail':'Items already reconciled for today!! Please Contact Admin'}, 400)
        if EndDayRecord.objects.filter(date=today_date, branch = branch, terminal=terminal).exists():
            return Response({'detail':'Items already reconciled for today!! Please Contact Admin'}, 400)

        return Response({'details':'ok'}, 200)
   
        
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from product.models import ProductCategory
from accounting.models import AccountLedger

class ProductCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Create a mutable copy of the request data
        type_id = data.pop('type', None)
        ledger_id = data.pop('ledger', [None])[0]
        opening_count = int(data.pop('opening_count', [None])[0])
        
        # Extract other fields from the request data
        title = data.pop('title', [None])[0]
        # slug = data.pop('slug', [None])[0]
        description = data.pop('description', [None])[0]
        price = float(data.pop('price', [0.0])[0])
        unit = data.pop('unit', [None])[0]
        barcode = data.pop('barcode', [None])[0]
        # group = data.pop('group', [None])[0]
        image = data.get('image', None)  # Get the image from the request data
        is_taxable = data.pop('is_taxable', None)[0] 
        reconcile = data.pop('reconcile', None)[0] 
        is_produced = data.pop('is_produced', None)[0] 
        is_billing_item = data.pop('is_billing_item', None)[0] 
        cost_price = float(data.pop('cost_price', [0.0])[0])  
        discount_exempt = data.pop('discount_exempt', None)[0] 
        minimum_stock = data.pop('minimum_stock', None)[0] 

        # Convert type_id to a ProductCategory instance
        try:
            product_type = ProductCategory.objects.get(title=type_id[0]) if isinstance(type_id, list) else ProductCategory.objects.get(title=type_id)
        except ProductCategory.DoesNotExist:
            return Response({'error': 'Invalid type ID'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ledger = AccountLedger.objects.get(id=ledger_id[0]) if isinstance(type_id, list) else AccountLedger.objects.get(id=ledger_id)
        except AccountLedger.DoesNotExist:
            return Response({'error': 'Invalid type ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data for the serializer
        product_data = {
            'title': title,
            'is_taxable':is_taxable,
            'reconcile': reconcile,
            'is_produced': is_produced,
            'description': description,
            'price': price,
            'cost_price': cost_price,
            'unit': unit,
            'barcode': barcode,
            'category': product_type.id,  # Using ID to pass to the serializer
            'image': image,  # Add the image to the product data
            'is_billing_item':is_billing_item,
            "ledger":ledger.id,
            "opening_count": opening_count,
            "minimum_stock": minimum_stock,
            'discount_exempt':discount_exempt

        }
        
        print(f"This is the product data {product_data} ")

        serializer = ProductSerializerCreate(data=product_data)
        if serializer.is_valid():
            product = serializer.save()
            response_data = {"id": product.id}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class ProductUpdateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        
        data = request.data.copy()  # Create a mutable copy of the request data
        print(data)
        type_id = data.pop('type', None)
        ledger = data.pop('ledger', None)
        
        # Check if 'image' field is provided in the request data
        if 'image' in data:
            if data['image'] != '':
            # If image is provided, use the provided value
                image_data = data['image']
            else :
                image_data = None
        else:
            if product.image != '':
                image_data = product.image
            else:
                image_data= None
            

        # Prepare the data for the serializer
        product_data = {
            'title': data.get('title', product.title),
            'slug': data.get('slug', product.slug),
            'description': data.get('description', product.description),
            'price': float(data.get('price', product.price)),
            'cost_price': float(data.get('cost_price', product.cost_price)),
            'unit': data.get('unit', product.unit),
            'barcode': data.get('barcode', product.barcode),
            # 'group': data.get('group', product.group),
            'image': image_data,
            'is_taxable': data.get('is_taxable', product.is_taxable),
            'reconcile': data.get('reconcile', product.reconcile),
            'is_produced': data.get('is_produced', product.is_produced),
            'is_billing_item': data.get('is_billing_item', product.is_billing_item),
            'opening_count': data.get('opening_count', product.opening_count),
            'discount_exempt': data.get('discount_exempt', product.discount_exempt),
            'minimum_stock': data.get('minimum_stock', product.minimum_stock),
        }

        if type_id:
            try:
                product_type = ProductCategory.objects.get(title=type_id[0])
                product_data['category'] = product_type.id
            except ProductCategory.DoesNotExist:
                return Response({'error': 'Invalid type ID'}, status=status.HTTP_400_BAD_REQUEST)
        if ledger:
            try:
                ledger = AccountLedger.objects.get(id=ledger[0])
                product_data['ledger'] = ledger.id
            except AccountLedger.DoesNotExist:
                return Response({'error': 'Invalid type Ledger ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializerCreate(product, data=product_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("Product Updated", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductDeleteAPIView(APIView):

    def patch(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        product.is_deleted = True
        product.status = False
        product.save()
        return Response("Product Deleted", status=status.HTTP_200_OK)
        
from api.serializers.product import ProductCategorySerializer
class CategoryAPIView(APIView):
    def get(self, request):
        categories = ProductCategory.objects.filter(status=True, is_deleted=False)

        serializer = ProductCategorySerializer(categories, many=True)
    

        return Response(serializer.data, 200)
        
class BranchWiseProduct(viewsets.ViewSet):
    
    def list(self, request, *args, **kwargs):
        
        branch_id = kwargs.get('branch')
        branch = Branch.objects.get(id=branch_id)
        branchstock_quantity_subquery_all = BranchStock.objects.filter(
            product=OuterRef('pk'),
            branch=branch
        ).values('product').annotate(total_quantity=Sum('quantity')).values('total_quantity')[:1]

        all_products = Product.objects.filter(
                is_deleted = False,
                is_billing_item=True
            )
        all_products_serializer = ProductSerializerList(all_products, many=True, context={"branch": branch_id})

        return Response(all_products_serializer.data)
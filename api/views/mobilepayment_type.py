from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from api.serializers.mobilepayment_type import MobilePaymentTypeSerializerCreate
from bill.models import MobilePaymentType

class MobilePaymentTypeCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Create a mutable copy of the request data
        
        # Extract other fields from the request data
        name = data.pop('name', [None])[0]
        company = data.pop('company', [None])[0]
        icon = data.get('icon', None)  # Get the image from the request data
        qr = data.get('qr', None)  # Get the image from the request data


        # Prepare the data for the serializer
        mobilepaymenttype_data = {
            'name': name,
            'company': company,
            'icon': icon,
            'qr': qr,

            # 'discount_exempt':discount_exempt

        }
        
        print(f"This is the product data {mobilepaymenttype_data} ")

        serializer = MobilePaymentTypeSerializerCreate(data=mobilepaymenttype_data)
        if serializer.is_valid():
            mobilepaymenttype = serializer.save()
            response_data = {"id": mobilepaymenttype.id}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class MobilePaymentTypeUpdateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        mobilepaymenttype_id = kwargs.get('pk')
        mobilepaymenttype = get_object_or_404(MobilePaymentType, pk=mobilepaymenttype_id)
        
        data = request.data.copy()  # Create a mutable copy of the request data
        print(data)
        # type_id = data.pop('type', None)
        # ledger = data.pop('ledger', None)
        
        # Check if 'image' field is provided in the request data
        if 'icon' in data:
            if data['icon'] != '':
            # If icon is provided, use the provided value
                icon_data = data['icon']
            else :
                icon_data = None
        else:
            if mobilepaymenttype.icon != '':
                icon_data = mobilepaymenttype.icon
            else:
                icon_data= None

        if 'qr' in data:
            if data['qr'] != '':
            # If qr is provided, use the provided value
                qr_data = data['qr']
            else :
                qr_data = None
        else:
            if mobilepaymenttype.qr != '':
                qr_data = mobilepaymenttype.qr
            else:
                qr_data= None
            

        # Prepare the data for the serializer
        mobilepaymenttype_data = {
            'name': data.get('name', mobilepaymenttype.name),
            'company': data.get('company', mobilepaymenttype.company),
            'icon': icon_data,
            'qr': qr_data,
        }

        serializer = MobilePaymentTypeSerializerCreate(mobilepaymenttype, data=mobilepaymenttype_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("Mobile Payment Updated", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MobilePaymentTypeDeleteAPIView(APIView):

    def patch(self, request, *args, **kwargs):
        mobilepayment_id = kwargs.get('pk')
        mobilepayment = get_object_or_404(MobilePaymentType, pk=mobilepayment_id)
        mobilepayment.is_deleted = True
        mobilepayment.status = False
        mobilepayment.save()
        return Response("MobilePaymentType Deleted", status=status.HTTP_200_OK)
    
from rest_framework.generics import ListAPIView, RetrieveAPIView
from api.serializers.mobilepayment_type import MobilePaymentSerializer
class MobilePaymentTypeList(ListAPIView):
    serializer_class = MobilePaymentSerializer
    pagination_class = None

    def get_queryset(self):
        return MobilePaymentType.objects.active()


class MobilePaymentTypeDetail(RetrieveAPIView):
    serializer_class = MobilePaymentSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return MobilePaymentType.objects.active()

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from discount.models import DiscountTable
from api.serializers.discount import DiscountSerilizer
from rest_framework import status


class DiscountApiView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        discount = DiscountTable.objects.filter(is_deleted=False, status=True)
        serilizer = DiscountSerilizer(discount, many=True)

        return Response(serilizer.data, status=status.HTTP_200_OK)
    
DiscountApiView=DiscountApiView.as_view()

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.serializers.organization import BranchSerializer, OrganizationSerializer
from datetime import datetime
from organization.models import Branch, Organization


class OrganizationApi(ReadOnlyModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.active()

    def list(self, request, *args, **kwargs):
        instance = Organization.objects.last()
        serializer_data = self.get_serializer(instance).data
        serializer_data['server_date'] = datetime.now().date()
        return Response(serializer_data)


class BranchApi(ReadOnlyModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.active().filter(is_central_billing=False).order_by('id')

from rest_framework import generics
from organization.models import PrinterSetting
from api.serializers.organization import PrinterSettingSerializer
from rest_framework.views import APIView
import jwt
from rest_framework import status
from organization.models import Terminal

class PrinterSettingListView(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data

        # jwt_token = request.META.get("HTTP_AUTHORIZATION")
        # jwt_token = jwt_token.split()[1]
        # try:
        #     token_data = jwt.decode(jwt_token, options={"verify_signature": False})  # Disable signature verification for claims extraction
        #     # You can access other claims as needed

        #     # Assuming "branch" is one of the claims, access it
        #     branch = token_data.get("branch")
        #     terminal_no = token_data.get("terminal")
        #     # token_type = token_data.get("token_type")


        #     # Print the branch
        #     print("Branch:", branch)
        #     print("Terminal:", terminal_no)
        # except jwt.ExpiredSignatureError:
        #     print("Token has expired.")
        # except jwt.DecodeError:
        #     print("Token is invalid.")
        branch = kwargs.get('branch_id')
        terminal_no = kwargs.get('terminal_no')

        ip = data['ip']
        port = data['port']
        url = data ['url']
        type = data['type']
        print_status = data['print_status']
        try:
            terminal_obj = Terminal.objects.get(terminal_no = int(terminal_no), status=True, is_deleted=False, branch=Branch.objects.get(id=branch, status=True, is_deleted=False))
        except Terminal.DoesNotExist:
            return Response({"detail":"Terminal does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        print(terminal_obj)
        try:
            PrinterSetting.objects.filter(terminal=terminal_obj, printer_location=type, is_deleted=False, status=True).delete()
            PrinterSetting.objects.create(ip=ip, port=port, url=url, terminal=terminal_obj, printer_location=type, print_status=print_status)
        except Exception as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail":"PrinterSetting created successfully"}, status=status.HTTP_200_OK)
        
    def get(self, request, *args, **kwargs):
        branch = kwargs.get('branch_id')
        terminal_no = kwargs.get('terminal_no')
        try:
            terminal_obj = Terminal.objects.get(terminal_no = int(terminal_no), status=True, is_deleted=False, branch=Branch.objects.get(id=branch, status=True, is_deleted=False))
        except Terminal.DoesNotExist:
            return Response({"detail":"Terminal does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        print(terminal_obj)
        try:
            printersettings = PrinterSetting.objects.filter(terminal=terminal_obj, is_deleted=False, status=True)
            serializer = PrinterSettingSerializer(printersettings, many=True)
            # PrinterSetting.objects.create(ip=ip, port=port, url=url, terminal=terminal_obj, printer_location=type, print_status=print_status)
        except Exception as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        branch = kwargs.get('branch_id')
        terminal_no = kwargs.get('terminal_no')
        try:
            terminal_obj = Terminal.objects.get(terminal_no = int(terminal_no), status=True, is_deleted=False, branch=Branch.objects.get(id=branch, status=True, is_deleted=False))
        except Terminal.DoesNotExist:
            return Response({"detail":"Terminal does not exists"}, status=status.HTTP_400_BAD_REQUEST)
        print(terminal_obj)
        try:
            PrinterSetting.objects.filter(terminal=terminal_obj, is_deleted=False, status=True).delete()
            # serializer = PrinterSettingSerializer(printersettings, many=True)
            # PrinterSetting.objects.create(ip=ip, port=port, url=url, terminal=terminal_obj, printer_location=type, print_status=print_status)
        except Exception as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail":"PrinterSettings have been deleted successfully"}, status=status.HTTP_200_OK)

from organization.cron import fetch_details
class TestMaster(APIView):
    def get(self, request):
        try:
            fetch_details()
        except Exception as e:
            print(e)
        
        return Response("success", 200)
        
from organization.models import Organization

class TrialBalanceToggleAPIView(APIView):
    def post(self, request, format=None):
        try:
            org = Organization.objects.first()
            org.show_zero_ledgers = not org.show_zero_ledgers
            org.save()
            return Response({'message': 'TrialBalnce non Zero Toggle successful'}, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response({'message': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
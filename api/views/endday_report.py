from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from datetime import datetime
from organization.models import EndDayDailyReport
from api.serializers.endday_report import EnddaySerializer

class EndDayReportAPIView(APIView):
    def post(self, request):
        # Retrieve fromDate and toDate from query parameters
        
        data = request.data
        branch = data.get('branch', None)

        if branch:
            queryset = EndDayDailyReport.objects.filter(branch__id=int(branch))
        else:
            queryset = EndDayDailyReport.objects.all()
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        # Retrieve end day reports based on date range
        if from_date and to_date:
            reports = []

            for report in queryset.order_by('created_at'):
                # report_datetime = datetime.strptime(report.created_at, '%Y-%m-%d %I:%M %p')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report.created_at.date() <= to_date.date():
                    reports.append(report)
            
            # Serialize the reports data if needed

        else:
            # Retrieve all reports if no date range specified
            reports = queryset.order_by('-created_at')

        serializer = EnddaySerializer(reports, many=True)

        # Return the response
        return Response(serializer.data, 200)
    
class EndDayReportDayWiseAPIView(APIView):
    def get(self, request):
        # Retrieve fromDate and toDate from query parameters
        from_date_str = request.GET.get('fromDate')
        to_date_str = request.GET.get('toDate')

        # Convert fromDate and toDate strings to datetime objects
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

        # Retrieve end day reports based on date range
        if from_date and to_date:
            reports = []

            daily_totals = {
                "Sun": 0,
                "Mon": 0,
                "Tue": 0,
                "Wed": 0,
                "Thu": 0,
                "Fri": 0,
                "Sat": 0,
            }

            for report in EndDayDailyReport.objects.all().order_by('created_at'):
                report_datetime = datetime.strptime(report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                # Check if the report_date falls within the specified range
                if from_date.date() <= report_datetime.date() <= to_date.date():
                    reports.append(report)

            
            print(reports)

            for daywise_report in reports:
                report_datetime = datetime.strptime(daywise_report.date_time, '%Y-%m-%dT%H:%M:%S.%f')
                day_of_week = report_datetime.weekday()
                
                # Convert day of the week index to day name
                day_name = report_datetime.strftime('%a')
                
                # Add total_sale to the corresponding day in daily_totals
                daily_totals[day_name] += daywise_report.total_sale
            
            # Serialize the reports data if needed

            # print(daily_totals)
            return Response(daily_totals, 200)
        else:
            # Retrieve all reports if no date range specified
            return Response("No date has been provided", 400)

        # serializer = EnddaySerializer(reports, many=True)

        # Return the response


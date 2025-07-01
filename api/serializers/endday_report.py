from organization.models import EndDayDailyReport

from rest_framework import serializers

class EnddaySerializer(serializers.ModelSerializer):
    class Meta:
        model=EndDayDailyReport
        exclude = [
            # "created_at",
            "updated_at",
            "status",
            "is_deleted",
            "sorting_order",
            "is_featured"
        ]
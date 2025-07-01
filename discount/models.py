from django.db import models
from root.utils import BaseModel
# Create your models here.
class DiscountTable(BaseModel):
    DISCOUNT_TYPE = (
        ("PCT", "PCT"),
        ("FLAT", "FLAT")
    )

    discount_name = models.CharField(max_length=200)
    discount_type = models.CharField(
        max_length=200, choices=DISCOUNT_TYPE
    )
    discount_amount = models.FloatField()

    def __str__(self) -> str:
        return self.discount_name

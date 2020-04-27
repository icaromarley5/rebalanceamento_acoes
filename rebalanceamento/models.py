from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(max_length=7,primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(validators=[MinValueValidator(0)])
    vpa = models.FloatField(validators=[MinValueValidator(0)])
    day = models.DateField()
    def __str__(self):
        return self.ticker
    class Meta:
        ordering = ["ticker"]
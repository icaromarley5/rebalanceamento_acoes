from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rebalanceamento import tickerData

fillDB = False

# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(max_length=7,primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField(validators=[MinValueValidator(0)])
    vpa = models.FloatField(validators=[MinValueValidator(0)])
    day = models.DateField()
    
    @classmethod
    def getOrCreate(cls, ticker):
        try:
            stock = cls.objects.get(ticker=ticker)
        except ObjectDoesNotExist:
            stock = None
        if stock:
            if stock.day != timezone.now().date(): # out of sync
                info = tickerData.findTickerInfo(ticker)
                if info: # exists, update db
                    stock.name = info['Nome']
                    stock.price = info['Preço']
                    stock.vpa = info['VPA']
                    stock.day = timezone.now().date()
                    try:
                        stock.save()
                    except Exception as e:
                        raise e # remover
                        pass
                else: # doesn't exist anymore, remove from db
                    try:
                        stock.delete()
                    except Exception as e:
                        raise e # remover
                        pass
                    stock = None 
        else: # not in db
            info = tickerData.findTickerInfo(ticker)
            if info: # never added before, add on db
                stock = cls(
                    ticker=ticker,
                    name=info['Nome'],
                    price=info['Preço'],
                    vpa=info['VPA'],
                    day = timezone.now().date())
                try:
                    stock.save()
                except Exception as e:
                    raise e # remover 
                    pass
        return stock 

    class Meta:
        ordering = ["ticker"]

import time
def fillStock():
    tickerList = tickerData.getAllTickers()
    #[Stock.getOrCreate(ticker) for ticker in tickerList]
    for ticker in tickerList:
        stock = Stock.getOrCreate(ticker)
        time.sleep(.1)
if fillDB:
    fillStock()
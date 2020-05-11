from django.utils import timezone
from django.conf import settings
import time
import threading

from rebalanceamento.models import Stock
from rebalanceamento import tickerData

import logging

logger = logging.getLogger('rebalanceamento')

def addStock(ticker, today):
    info = tickerData.findTickerInfo(ticker)
    if info: # exists, update db
        try:
            stock = Stock.objects.get(ticker=ticker)
            stock.ticker = ticker
            stock.name = info['Nome']
            stock.price = info['Preço']
            stock.vpa = info['VPA']
            stock.pvp = info['PVP']
            stock.day = today
            stock.save()
        except:
            stock = Stock(
                ticker=ticker,
                name=info['Nome'],
                price=info['Preço'],
                vpa=info['VPA'],
                pvp = info['PVP'],
                day=today
            ).save()

def watcherFillDB():
    while True:
        now = timezone.now()
        hour = now.hour
        today = now.date()

        oldStocks = Stock.objects.filter(day__lt=today)
        newStocks = Stock.objects.filter(day=today)
        if oldStocks or not newStocks:
            logger.info(f'({now}) WatcherDB: Updating stock info')
            for ticker in tickerData.getAllTickers():
                addStock(ticker, today)
                time.sleep(.1)
            for stock in Stock.objects.filter(day__lt=today):
                stock.delete()
            logger.info(
                f'({timezone.now()}) WatcherDB: Update completed'
            )
        
        toSleep = (25 - hour) * 60 * 60
        logger.info(
            f'({timezone.now()}) WatcherDB: Hours to sleep: {toSleep/3600}'
        )
        time.sleep(toSleep)

if settings.SERVER:
    threading.Thread(
        target=watcherFillDB, 
        daemon=True
    ).start()
from django.db import models

# Create your models here.

'''Here is the model for the user with a username and initial balance
'''
class User(models.Model):
    username= models.CharField(max_length=100)
    Initial_balance=models.IntegerField()
'''
Here is the model for the stock with ticker and price the "ticker" is unique and combination of alphabet,letter etc
'''
class Stock(models.Model):
    ticker=models.CharField(max_length=50, unique=True)
    price=models.DecimalField(max_digits=20,decimal_places=2)
    
'''
Here is the model for the transaction user, ticker, transaction_type, and transaction_volume, transaction_price, timestamp as inputs
'''
#first make a transaction type class
class TransactionType(models.TextChoices):
        BUY = 'buy', 'Buy'
        SELL = 'sell', 'Sell'
        
class Transaction(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    ticker=models.ForeignKey(Stock,on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=4,
        choices=TransactionType.choices,
        default=TransactionType.BUY,
    )
    transaction_volume=models.PositiveIntegerField()
    transaction_price=models.DecimalField(max_digits=10,decimal_places=2)
    time=models.DateTimeField(auto_now_add=True)
    
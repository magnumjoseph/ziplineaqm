# ziplineaqm

## To install:

```shell
$ pip install git+https://github.com/magnumjoseph/ziplineaqm.git
```

**Note:** In order to use this library, you also need to download
the most updated version of ``lib/commonalgo``.

## To use:

```python
from zipline.finance import commission, slippage

context.set_commission(commission.PerTransaction())
context.set_slippage(slippage.AQMVolumeShareSlippage(price_impact=0, volume_limit=1))
```

Currently the ``PerTransaction`` model only handles ``commission_type=1, 2``; 
for other cases, you need to overwrite the model accordingly (an example):

```python
class MyPerTransaction(commission.PerTransaction):
	def __init__(self):
		super(MyPerTransaction, self).__init__()

	def calculate(self, order, transaction):
		"""
        Specify my own commission model.
        """
		commission = transaction.commission
		commission_type = transaction.commission_type
		price = transaction.price
		amount = transaction.amount
		if commission_type == float(1):  # cost per dollar
			return abs(amount) * price * commission
		elif commission_type==float(2): # cost per lot
			return abs(amount) * commission
		else: # take care of all other commission types
			return 0.0
```
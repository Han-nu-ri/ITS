start cmd /k python .\InOperate\priceInformer.py

timeout 5

start cmd /k python .\InOperate\calculateRSI.py

timeout 5

start cmd /k python .\InOperate\OrderCoinByRSI.py
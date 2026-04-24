import sys
try:
    import pandas
    print("pandas:", pandas.__version__)
except Exception as e:
    print("pandas: MISSING -", e)

try:
    import numpy
    print("numpy:", numpy.__version__)
except Exception as e:
    print("numpy: MISSING -", e)

try:
    import akshare
    print("akshare:", akshare.__version__)
except Exception as e:
    print("akshare: MISSING -", e)

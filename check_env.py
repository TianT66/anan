# -*- coding: utf-8 -*-
import site
import sys
print("Python:", sys.version)
print("User site:", site.getusersitepackages())
print("Temp dir:", site.gettempdir())

# Check if pandas/numpy installed
try:
    import pandas
    print("pandas:", pandas.__version__)
except:
    print("pandas: NOT INSTALLED")

try:
    import numpy
    print("numpy:", numpy.__version__)
except:
    print("numpy: NOT INSTALLED")

try:
    import akshare
    print("akshare:", akshare.__version__)
except:
    print("akshare: NOT INSTALLED")

import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)

try:
    import numpy as np
    print("NumPy:", np.__version__)
except ImportError as e:
    print("NumPy:", e)

try:
    import torch
    print("PyTorch:", torch.__version__)
except ImportError as e:
    print("PyTorch:", e)

try:
    import sklearn
    print("Scikit-Learn:", sklearn.__version__)
except ImportError as e:
    print("Scikit-Learn:", e)

try:
    import scipy
    print("SciPy:", scipy.__version__)
except ImportError as e:
    print("SciPy:", e)

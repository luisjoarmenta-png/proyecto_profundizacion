

import platform
from importlib import metadata

libreria = "pandas"
version= metadata.version(libreria)

print ("Version de python:", platform.python_version())
print("Version de pandas:", version)
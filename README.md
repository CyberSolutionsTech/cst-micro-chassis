### Cst-Micro-Chassis

---

Cst-Micro-Chassis is a chassis framework for creating REST-ful APIs based on Flask and Flask-Restful. 

The main topics covered are: 

 1. A uniform API response format
 2. API pagination
 3. Logging
 4. Health check

---
#### Installation
```shell
pip install cst-micro-chassis
```

---
#### Usage


Import and initialize using a flask app (as you would usually do with any other flask extension)

```python
from flask import Flask
from cst_micro_chassis import CstMicroChassis

app = Flask(__name__)
CstMicroChassis.init_app(app)

```

















#### Contributing
 - run the tests: 
```shell
make test
```
this will set up a virtual environment with [tox](https://tox.readthedocs.io) and run the unittest on Python3.9 

If you want to run the test using a different interpreter version, update the [Makefile](../Makefile)'s `test` target, changing `tox -e py39` to either `tox -e py37` or `tox -e py38`

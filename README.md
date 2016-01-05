handsontables for jupyter
===============================

version number: 0.0.1
author: David Fullmer

Overview
--------

Integrate handsontables with pandas for jupyter with two way bindings.

Installation / Usage
--------------------

To install use pip:

    $ pip install handsontablesjs


Or clone the repo:

    $ git clone https://github.com/techmuch/jupyter-handsontables.git
    $ python setup.py install    
    
Contributing
------------

TBD

Example
-------

    import numpy as np
    import pandas as pd
    from handsontablesjs import *
    
    data = np.random.randint(size=(3, 5), low=100, high=900)
    df = pd.DataFrame(data)
    
    ht = HandsonTable(value=df)
    
Simply use ht to view the handsontable or ht.value to view the pandas dataframe
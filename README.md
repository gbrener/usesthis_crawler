# usesthis_crawler

This is a crawler that scrapes usesthis.com/interviews and stores the results in a local database. The scraped information includes parts of the transcript, details about the person being interviewed, and the tools they use to do their jobs.

**Note: Python 2.7 recommended. Not compatible with Python 3.**

To install:

    python setup.py install

*Conda users* should also do the following ([here's why](https://cryptography.io/en/latest/installation/#building-cryptography-with-conda)):

    pip uninstall cryptography
    export DYLD_LIBRARY_PATH="$HOME/anaconda/lib" # aka LD_LIBRARY_PATH on Linux
    pip install cryptography


To run:

    crawl-usesthis [-h] [-t] [-s] [-n]
                   [-l {INFO,ERROR,WARN,DEBUG}]
                   [-d DB_PATH] [-r] [-v]

Example:

    crawl-usesthis -d interviews.db


For help:

    crawl-usesthis -h


To test:

    pip install hypothesis
    python setup.py nosetests

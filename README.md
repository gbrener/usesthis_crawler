# usesthis_crawler

To install:

    python setup.py install


To run:

    crawl-usesthis [-h] [-t] [-s] [-n]
                   [-l {INFO,ERROR,WARN,DEBUG}]
                   [-d DB_PATH] [-r] [-v]

Example:

    crawl-usesthis -d interviews.db


For help:

    crawl-usesthis -h


To develop:

    python setup.py nosetests
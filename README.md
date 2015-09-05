# usesthis_crawler

Crawler that scrapes usesthis.com/interviews and stores the results in a local database. The database contains information about each interview, including the interview transcript, details about the person being interviewed, and the tools they use to do their jobs.

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


To test:

    python setup.py nosetests

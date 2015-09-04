import logging
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger('usesthis_crawler')
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(u'%(message)s')
)
logger.addHandler(console_handler)

Session = sessionmaker()

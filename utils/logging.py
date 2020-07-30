import logging
import sys

DEBUG = logging.DEBUG
NOTICE = 15

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("%(message)s"))
stdout_handler.setLevel(NOTICE)

logger = logging.getLogger("dbt")
logger.addHandler(stdout_handler)
logger.setLevel(DEBUG)

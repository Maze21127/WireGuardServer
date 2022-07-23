import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler("logs/logs.txt")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

import os

TARGET_HOST = os.getenv('AD_HOST', 'zhaw.ch')
DB_HOST = os.getenv('DB_HOST')
BATCH_INTERVAL = int(os.getenv('BATCH_INTERVAL', 2592000))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LIMIT_RUN = os.getenv('LIIMIT_RUN', -1)
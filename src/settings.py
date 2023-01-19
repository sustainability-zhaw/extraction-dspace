import os

TARGET_HOST = os.getenv('AD_HOST', 'https://digitalcollection.zhaw.ch/oai/request/') # url to the oai-pmh api'
DB_HOST = os.getenv('DB_HOST', 'localhost:8080') #http://dgraph_standalone:8080) # url to the grapg database
BATCH_INTERVAL = int(os.getenv('BATCH_INTERVAL', 2592000))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LIMIT_BATCH = int(os.getenv('LIMIT_BATCH', -1))  # define how many batches to process at max, -1 for no limit

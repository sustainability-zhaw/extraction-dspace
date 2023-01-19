import os

TARGET_HOST = os.getenv('AD_HOST', 'https://digitalcollection.zhaw.ch/oai/request/') # url to the oai-pmh api'
DB_HOST = os.getenv('DB_HOST', 'http://localhost:8080/graphql') # url to the grapg database
PUBDB_UPDATE_INTERVAL = int(os.getenv('PUBDB_UPDATE_INTERVAL', 2592000)) # time to wait between updates of the publication database
OAI_REQUEST_INTERVAL = int(os.getenv('OAI_REQUEST_INTERVAL', 0)) # time to wait between requests to the oai-pmh api
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LIMIT_BATCH = int(os.getenv('LIMIT_BATCH', 2)) # define how many batches to process at max, -1 for no limit

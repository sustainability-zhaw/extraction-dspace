import os

##
# IMPORTANT NOTE
# 
# Any default values in this file are only INFORMATIVE. The actual default values are defined in the Dockerfile.

TARGET_HOST = os.getenv('TARGET_HOST', '') # url to the oai-pmh api'
TARGET_PATH = os.getenv('TARGET_PATH', '/oai/request/')
DB_HOST = os.getenv('DB_HOST', 'http://localhost:8080') # url to the grapg database
DB_PATH = os.getenv('DB_PATH', '/graphql') # url to the grapg database
PUBDB_UPDATE_INTERVAL = int(os.getenv('PUBDB_UPDATE_INTERVAL', 2592000)) # time to wait between updates of the publication database
OAI_REQUEST_INTERVAL = int(os.getenv('OAI_REQUEST_INTERVAL', 0)) # time to wait between requests to the oai-pmh api
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LIMIT_BATCH = int(os.getenv('LIMIT_BATCH', 2)) # define how many batches to process at max, -1 for no limit

# helper dictionary to get the departmental affiliation

DepartmentCollections = {
    "com_11475_1": "L",
    "com_11475_2": "P",
    "com_11475_3": "G",
    "com_11475_4": "N",
    "com_11475_5": "R",
    "com_11475_6": "T",
    "com_11475_7": "W",
    "com_11475_8": "S",
    "com_11475_1074": "A",
    "com_11475_1077": "V"
}

# this mapping should come from a config file and the cross matched with dspace collections

DepartmentNames = {
    "Angewandte Linguistik": "L",
    "Angewandte Psychologie": "P",
    "Gesundheit": "G",
    "Life Sciences und Facility Management": "N",
    "Rektorat und Ressorts": "R",
    "School of Engineering": "T",
    "School of Management and Law": "W",
    "Soziale Arbeit": "S",
    "Architektur, Gestaltung und Bauingenieurwesen": "A",
    "Finanzen & Services": "V"
} 

import os
import json

_settings = {
    "DB_HOST": os.getenv('DB_HOST', 'http://localhost:8080'),
    "DB_PATH": os.getenv('DB_PATH', '/graphql'),
    "TARGET_HOST": os.getenv('TARGET_HOST', 'https://digitalcollection.zhaw.ch'),
    "TARGET_PATH": os.getenv('TARGET_PATH', '/oai/request/'),
    "PUBDB_UPDATE_INTERVAL": int(os.getenv('PUBDB_UPDATE_INTERVAL', 2592000)),
    "OAI_REQUEST_INTERVAL": int(os.getenv('OAI_REQUEST_INTERVAL', 180)),
    "LOG_LEVEL": os.getenv('LOG_LEVEL', ' DEBUG'),
    "LIMIT_BATCH": int(os.getenv('LIMIT_BATCH', -1)), # define how many batches to process at max, -1 for no limit
    "MQ_HOST": os.getenv("MQ_HOST", "mq"),
    "MQ_EXCHANGE": os.getenv("MQ_EXCHANGE", "zhaw-km"),
    "MQ_HEARTBEAT": int(os.getenv("MQ_HEARTBEAT", 6000)),
    "MQ_TIMEOUT": int(os.getenv("MQ_TIMEOUT", 3600)),
    "MQ_USER": os.getenv("MQ_USER", "extraction-dspace"),
    "MQ_PASS": os.getenv("MQ_PASS", "guest")
}

if os.path.exists('/etc/app/config.json'):
    with open('/etc/app/config.json') as secrets_file:
        config = json.load(secrets_file)
        for key in config.keys():
            if config[key] is not None:
                _settings[str.upper(key)] = config[key]

## 
# IMPORTANT NOTE
# 
# Any default values in this file are only INFORMATIVE. The actual default values are defined in the Dockerfile.

TARGET_HOST = _settings['TARGET_HOST'] # url to the oai-pmh api'
TARGET_PATH = _settings['TARGET_PATH']
DB_HOST = _settings['DB_HOST'] # url to the grapg database
DB_PATH = _settings['DB_PATH'] # url to the grapg database
PUBDB_UPDATE_INTERVAL = _settings['PUBDB_UPDATE_INTERVAL'] # time to wait between updates of the publication database
OAI_REQUEST_INTERVAL = _settings['OAI_REQUEST_INTERVAL']  # time to wait between requests to the oai-pmh api
LOG_LEVEL = _settings['LOG_LEVEL']
LIMIT_BATCH = _settings['LIMIT_BATCH']
MQ_HOST = _settings['MQ_HOST']
MQ_EXCHANGE = _settings['MQ_EXCHANGE']
MQ_HEARTBEAT = _settings['MQ_HEARTBEAT']
MQ_TIMEOUT = _settings['MQ_TIMEOUT']
MQ_USER = _settings['MQ_USER']
MQ_PASS = _settings['MQ_PASS']

# helper dictionary to get the departmental affiliation

DepartmentCollections = {
    "com_11475_1": "department_L",
    "com_11475_2": "department_P",
    "com_11475_3": "department_G",
    "com_11475_4": "department_N",
    "com_11475_5": "department_R",
    "com_11475_6": "department_T",
    "com_11475_7": "department_W",
    "com_11475_8": "department_S",
    "com_11475_1074": "department_A",
    "com_11475_1077": "department_V"
}

# this mapping should come from a config file and the cross matched with dspace collections

DepartmentNames = {
    "Angewandte Linguistik": "department_L",
    "Angewandte Psychologie": "department_P",
    "Gesundheit": "department_G",
    "Life Sciences und Facility Management": "department_N",
    "Rektorat und Ressorts": "department_R",
    "School of Engineering": "department_T",
    "School of Management and Law": "department_W",
    "Soziale Arbeit": "department_S",
    "Architektur, Gestaltung und Bauingenieurwesen": "department_A",
    "Finanzen & Services": "department_V"
} 

# integration packages
import settings
import logging

# packaeges for dgraph and OAI interface
import requests
import re
from bs4 import BeautifulSoup
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json

# start
logger = logging.getLogger('extract-dspace')


async def get_last_dgraph_update_timestamp(client):
    """
    The get_last_dgraph_update_timestamp function returns the last time that Dgraph was updated.
    It does this by querying the dgraph database for a queryInfoObject with a dateUpdate field, and then returning 
    the value of that field.
    
    :param client: Access the dgraph api
    :return: The date of the last update to the dgraph database / else None
    """
    query = gql(
        """
        query {
            queryInfoObjectType(filter: { name: { eq: "publications" } }) {
                objects(order: { desc: dateUpdate }, first: 1) {
                    dateUpdate
                }
            }
        }
        """
    )
    result = await client.execute_async(query)
    # print(result)
    if len(result['queryInfoObjectType'][0]["objects"]) > 0:
        return result['queryInfoObjectType'][0]["objects"][0]['dateUpdate']
    else:
        return None


def get_single_chunk_oai_records_by_date(oai_url, datestamp=None, resumption_token=None):
    """
    The get_single_chunk_oai_records_by_date function takes a URL for an OAI-PMH endpoint,
    a datestamp (in the form YYYY-MM-DD), and optionally a resumption token. 
    If no resumption token is provided, it will request the first chunk of records from that date. 
    If a resumption token is provided, it will request the next chunk of records after that date.  
    The function returns an XML object containing all OAI records returned by the query.
    
    :param oai_url: Specify the oai-pmh endpoint of the repository
    :param datestamp: Specify a date from which to retrieve the records i.e. '2023-01-13'
    :param resumption_token: Retrieve the next chunk of records
    :return: A beautifulsoup object containing the xml response
    """

    if datestamp is None: # set some default datestamp
        datestamp = '1900-01-01T00:00:00Z'

    if resumption_token is None: # no resumtion token, so get first chunk
        params = {'metadataPrefix': 'oai_dc', 'from': datestamp} # The metadataPrefix - a string to specify the metadata format in OAI-PMH requests issued to the repository
    else: # there is a resumption token, so get the next chunk
        params= {'resumptionToken': resumption_token}

    params['verb'] = 'ListRecords'
    resp = requests.get(oai_url, params=params)
    oaixml = BeautifulSoup(resp.content, "lxml-xml")

    return oaixml


def get_entity_from_xml_record_entity(record, entity):
    """
    The get_entity_from_xml_record_entity function is used to get a specific entry from the xml record.
    The function takes two arguments: record and entity. The record is the xml record and the entity is the specific entry that you want to get.
    
    :param record: The xml record entity
    :param entity: The specific entry that you want to get
    :return: A list of the specific entry
    """
    if len(record.metadata.find_all(entity)) > 0: # check if there is the entity
        if len(record.metadata.find_all(entity)[0].contents) > 0: # check if there is some actual content for the entity
            entity_list = [record.metadata.find_all(entity)[i].contents[0] for i in range(len(record.metadata.find_all(entity)))]
        else: # if there no content for the entity, then return an empty list
            entity_list = []
    else: # if there is no entity, then return an empty list
        entity_list = []    
    return entity_list


def get_deptcollection_from_xml_record_entity(record):
    """
    The get_deptcollection_from_xml_record_entity function is used to extract the department from a record's header.
    It uses a lookup table from settings.py to map the collection id  to the internal department label. The 
    result is a list of department associations. Any collection that is not mapped is ignored. 
    
    :param record: The xml record entity
    :return: A list of mapped department relations for the specific entry
    """
    entity = 'setSpec' 
    entity_list = []

    # check if there is is an entity with some actual content 
    if len(record.header.find_all(entity)) > 0: 
        for i in range(len(record.header.find_all(entity))):
            entity_content = "".join(record.header.find_all(entity)[i].contents)
            if entity_content in settings.DepartmentCollections:
                entity_list.append({ "id": settings.DepartmentCollections[entity_content] })

    return entity_list

def clean_string(string):
    """
    The clean_string function takes a string as an argument and returns the same string.
    
    This has to be done, as the string shall not interfere with the query string constructed for the graph database.
    However, there should be a more elegant way to handel this issue.

    :param string: Pass the string that is being cleaned
    :return: A string that escapes the following characters: \n, \r, \t, \", \\, \W, \C, \P, \A, \%, \i
    """
    string = string.strip()

    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    string = string.replace('\"', '\\"')
    string = string.replace('\\ ', '\\\\ ')
        
    string = string.replace('\W', '\\\\W')
    string = string.replace('\C', '\\\\C')
    string = string.replace('\P', '\\\\P')
    string = string.replace('\A', '\\\\A')
    string = string.replace('\%', '\\\\%')
    string = string.replace('\i', '\\\\i')

    string = string.replace('\\\\\\\\"', '\\"') # this is a pattern found in some title
    # there should be a more elegant way to do this ... i.e. a regex pattern
    return string


def gen_record_dict(record):
    """
    The gen_record_dict function takes a single XML record from the ZHAW Digital
    Collection and returns a dictionary with all of its information. The function
    takes one argument, which is an xml.etree object representing the record in 
    question.
    
    :param record: xml record from the oai-api
    :return: A dictionary that can be used to create a new publication in the graph database
    """

    record_department_list = get_deptcollection_from_xml_record_entity(record)
    
    # get information from the xml record
    record_identifier_list = record.header.identifier.contents
    record_titel_list = get_entity_from_xml_record_entity(record, 'dc:title')
    record_dc_creator_list = get_entity_from_xml_record_entity(record, 'dc:creator')
    record_dc_subject_list = get_entity_from_xml_record_entity(record, 'dc:subject')
    record_dc_description_list = get_entity_from_xml_record_entity(record, 'dc:description')
    record_dc_date_list = get_entity_from_xml_record_entity(record, 'dc:date')
    record_dc_type_list = get_entity_from_xml_record_entity(record, 'dc:type')
    #record_dc_identifier_list = get_entity_from_xml_record_entity(record, 'dc:identifier')
    record_dc_language_list = get_entity_from_xml_record_entity(record, 'dc:language')
    # record_dc_rights_list = get_entity_from_xml_record_entity(record, 'dc:rights')
    # record_dc_publisher_list = get_entity_from_xml_record_entity(record, 'dc:publisher')
    # record_dc_relation_list = get_entity_from_xml_record_entity(record, 'dc:relation')
    # record_dc_publisher_list = get_entity_from_xml_record_entity(record, 'dc:publisher')
    record_datestamp = record.datestamp.contents[0]
    # get title of the record
    if len(record_titel_list) > 0:
        record_title = record_titel_list[0]
        record_title = clean_string(record_title)
    else:
        record_title = ''   
    # get year of the record ... i.e. last entry in the list
    record_year = int(record_dc_date_list[-1].split('-')[0])

    # record_dc_subject_list
    # get list of subjects, i.e. number (3 digit): description
    # record_class_list = [subject for subject in record_dc_subject_list if subject.find('[0-9]:') != -1]
    record_class_list = [subject for subject in record_dc_subject_list if re.match('\d\d\d: ', subject) is not None]
    # get keywords from the subjects
    record_keyword_list = [subject for subject in record_dc_subject_list if re.match('\d\d\d: ', subject) is None]

    # get url to the record in the digital collection
    record_url = 'https://digitalcollection.zhaw.ch/handle/' + record_identifier_list[0].split(':')[-1]

    # get language of the record, use simply first entry
    record_language = record_dc_language_list[0]

    # get type of the record, use simply first entry
    # record_categoty = record_dc_type_list[0]
    # get type of the record, use simply first entry
    record_subtype = record_dc_type_list[0]

    # get abstract for record ... i.e. last entry in the list
    if len(record_dc_description_list) > 0:
        # print(record_dc_description_list)
        record_abstract = record_dc_description_list[-1]
        record_abstract = clean_string(record_abstract)
    else:
        record_abstract = ''

    record_dict = {
        'title': record_title.strip(),
        'dateUpdate': record_datestamp,
        'authors': [{'fullname': clean_string(record_dc_creator_list[i])} for i in range(len(record_dc_creator_list))], # [{ fullname: "Föhn, Martina" }]
        'abstract': record_abstract,
        'year': record_year, # 2022
        'keywords':  [{'name': clean_string(record_keyword_list[i])} for i in range(len(record_keyword_list))], # [{ name: "Forest therapy" }, { name: "Health" }, { name: "Mindfulness" }, { name: "Distress" }, { name: "Forest medicine" }, { name: "Shinrin yoku" }, { name: "Cortisol" }, { name: "Forest bathing" }]
        'class': [{'id': record_class_list[i].split(':')[0].strip(), 'name': record_class_list[i].split(':')[1].strip()} for i in range(len(record_class_list))], # [{ id: "615" name: "Pharmakologie und Therapeutik" }]
        'link': record_url.strip(),# "https://digitalcollection.zhaw.ch/handle/11475/23944",
        'language': record_language.strip(), #"de",
        'category': {'name': 'publications'},
        'subtype':  {'name': record_subtype.strip()},
        'departments': record_department_list
    }
    return record_dict

async def add_records_to_graphdb_with_updateDate(oaixml, client, channel):
    """
    The add_records_to_graphdb function takes in a chunk of records and adds them to the graphdb database.
    :param oaixml: A chunk of records
    :return: (# of inserted records, # of deleted records)
    """
    
    inserted_records = 0
    deleted_records = 0

    my_query = """
    mutation addInfoObject($record: [AddInfoObjectInput!]!) { 
        addInfoObject(input: $record, upsert: true) {
            infoObject { 
                link
            } 
        } 
    }
    """

    recquery = gql(my_query)

    # add chunk of records to the database
    for record in oaixml.find_all('record'):
        # check header if record is deleted ... indicated by tag: status = deleted
        record_deleted = False
        if len(record.header.attrs) > 0:
            if record.header['status'] == 'deleted':
                # print('Record is deleted')
                record_deleted = True
                deleted_records += 1

        if not record_deleted:  
            record_dict = gen_record_dict(record)  # extract information for current record

            result = await client.execute_async(recquery, variable_values = {"record": [record_dict]})

            logger.debug(result)

            channel.basic_publish(
                settings.MQ_EXCHANGE,
                routing_key="importer.object",
                body=json.dumps({ "link": record_dict["link"] })
            )
            
            inserted_records += 1
    return inserted_records, deleted_records


async def run(channel, resumption_token=None):
    logger.info("run service function")

    oai_url = settings.TARGET_HOST + settings.TARGET_PATH #' https://digitalcollection.zhaw.ch/oai/request/' # url to the oai-pmh api
    graphdb_endpoint = settings.DB_HOST + settings.DB_PATH # 'http://localhost:8080/graphql' # url to the graphdb endpoint

    logger.debug(oai_url)
    logger.debug(graphdb_endpoint)

    transport = AIOHTTPTransport(url=graphdb_endpoint) # Select your transport with a defined url endpoint
    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # get_last_dgraph_update_timestamp
    if resumption_token is None:
        last_update_timestamp = await get_last_dgraph_update_timestamp(client)
        if last_update_timestamp is not None:
            logger.info('Last update timestamp in graphDB: ' + last_update_timestamp)
        else:
            logger.info('No last update timestamp in graphDB ... default set to 1900-01-01T00:00:00Z')
    else: 
        last_update_timestamp = None
    
    try: 
        # chunk of records that have been updated since the last update
        oaixml = get_single_chunk_oai_records_by_date(oai_url, datestamp=last_update_timestamp, resumption_token=resumption_token)
        token = oaixml.resumptionToken
    except:
        return None

    # add chunk of records to the database
    inserted_records, deleted_records = await add_records_to_graphdb_with_updateDate(oaixml, client=client, channel=channel)

    logger.info('Number of inserted records: ' + str(inserted_records))
    logger.info('Number of deleted records: ' + str(deleted_records))
    logger.info('finished service function')
    return token
    
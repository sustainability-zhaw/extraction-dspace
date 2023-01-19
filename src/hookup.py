# integration packages
import settings
import logging

# packaeges for dgraph and OAI interface
import requests
import re
from bs4 import BeautifulSoup
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

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
            queryInfoObject(order: {desc: dateUpdate}, first: 1) {
                dateUpdate     
            }
        }
        """
    )
    result = await client.execute_async(query)
    # print(result)
    if len(result['queryInfoObject']) > 0:
        return result['queryInfoObject'][0]['dateUpdate']
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
    :return: A beautifulsoup object
    :doc-author: Trelent
    """

    if not datestamp: # set some default datestamp
        datestamp = '1900-01-01T00:00:00Z'

    verb = 'ListRecords'
    if resumption_token is None: # no resumtion token, so get first chunk
        params = {'verb': verb, 'metadataPrefix': 'oai_dc', 'from': datestamp} # The metadataPrefix - a string to specify the metadata format in OAI-PMH requests issued to the repository
        resp = requests.get(oai_url, params=params)
        oaixml = BeautifulSoup(resp.content, "lxml-xml")
    else: # there is a resumption token, so get the next chunk
        params={'verb': verb, 'resumptionToken': resumption_token}
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


def clean_string(string):
    """
    The clean_string function takes a string as an argument and returns the same string.
    
    This has to be done, as the string shall not interfere with the query string constructed for the graph database.
    However, there should be a more elegant way to handel this issue.

    :param string: Pass the string that is being cleaned
    :return: A string that escapes the following characters: \n, \r, \t, \", \\, \W, \C, \P, \A, \%, \i
    """
    
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
        'title': record_title,
        'datestamp': record_datestamp,
        'authors': [{'fullname': record_dc_creator_list[i]} for i in range(len(record_dc_creator_list))], # [{ fullname: "Föhn, Martina" }]
        'persons': [], #[{ LDAPDN: "cn=fhia" }]
        'abstract': record_abstract,
        'year': record_year, # 2022
        'keywords':  [{'name': record_keyword_list[i]} for i in range(len(record_keyword_list))], # [{ name: "Forest therapy" }, { name: "Health" }, { name: "Mindfulness" }, { name: "Distress" }, { name: "Forest medicine" }, { name: "Shinrin yoku" }, { name: "Cortisol" }, { name: "Forest bathing" }]
        'class': [{'id': record_class_list[i].split(':')[0], 'name': record_class_list[i].split(':')[1]} for i in range(len(record_class_list))], # [{ id: "615" name: "Pharmakologie und Therapeutik" }]
        'link': record_url,# "https://digitalcollection.zhaw.ch/handle/11475/23944",
        'language': record_language, #"de",
        'category': {'name': 'publications'},
        'subtype':  {'name': record_subtype}
    }
    return record_dict


def gen_mutation_string_for_authors(authors):
    """
    The gen_mutation_string_for_authors function takes a list of dictionaris of authors
    and returns a string with the following format: [{fullname: "Cantoni, Marco"}, {fullname: "Holzer, Lorenz"}]
    
    :param authors: A list of dictionaries of authors [{'fullname': 'Cantoni, Marco'}, {'fullname': 'Holzer, Lorenz'}]
    :return: A string with the following format:
        [{fullname: "Cantoni, Marco"}, {fullname: "Holzer, Lorenz"}]
    """
    authors_string = '[' + ', '.join(['{fullname: "' + clean_string(author['fullname']) + '"}' for author in authors]) + ']'
    return authors_string


def gen_mutation_string_for_keywords(keywords):
    """
    The gen_mutation_string_for_keywords function takes a list of dictionaris of keywords
    and returns a string with the following format: [{name: "Forest therapy"}, {name: "Health"}]

    :param keywords: A list of dictionaries of keywords [{'name': 'Forest therapy'}, {'name': 'Health'}]
    :return: A string with the following format:
        [{name: "Forest therapy"}, {name: "Health"}]
    """
    keywords_string = '[' + ', '.join(['{name: "' + clean_string(keyword['name']) + '"}' for keyword in keywords]) + ']'
    return keywords_string


def gen_mutation_string_for_classes(classes):
    """
    The gen_mutation_string_for_classes function takes a list of dictionaris of classes
    and returns a string with the following format: [{id: "615", name: "Pharmakologie und Therapeutik"}]

    :param classes: A list of dictionaries of classes [{'id': '615', 'name': 'Pharmakologie und Therapeutik'}]
    :return: A string with the following format:
        [{id: "615", name: "Pharmakologie und Therapeutik"}]
    """
    classes_string = '[' + ', '.join(['{id: "' + class_['id'] + '", name: "' + class_['name'] + '"}' for class_ in classes]) + ']'
    return classes_string


def gen_pub_mutation_string_update(title, authors, abstract,link, year, language, keywords, classes, subtype, update_datetime):
    """
    The gen_pub_mutation_string function takes in a dictionary of information about a publication and returns
    a string that can be used to add the publication to the database. The string is formatted in the following way:
    mutation {
        addInfoObject(input: [{
            title: "Forest bathing and its effects on stress and health: A systematic review",
            authors: [{fullname: "Cantoni, Marco"}, {fullname: "Holzer, Lorenz"}],
            link: "https://digitalcollection.zhaw.ch/handle/11475/23944",
            year: 2022,
            keywords: [{name: "Forest therapy"}, {name: "Health"}],
            class: [{id: "615", name: "Pharmakologie und Therapeutik"}],
            language: "de",
            category: {name: "publications"},
            subtype: {name: "Journal Article"}
            dateUpdate: "1900-01-01T00:00:00Z" 
        }],
            upsert: true) {
                infoObject {
                    title
                    link
                    year
                }
            }    
        }       
    
    :param title: Set the title of the publication
    :param authors: Generate the mutation string for authors
    :param abstract: Generate the abstract field of the publication
    :param link: Link the publication to a specific page on the website
    :param year: Filter the publications
    :param language: Determine the language of the publication
    :param keywords: Generate a string that can be used in the mutation query
    :param classes: Specify the class of the publication
    :param subtype: Specify the type of publication
    :param update_datetime: Specify the date and time of the last update
    :return: The string for the mutation that will add a publication to the database
    """
    
    query_string = """
        mutation {
            addInfoObject(input: [{
        """ + \
        'title: "' + title + '",\n' + \
        'authors: ' + gen_mutation_string_for_authors(authors) + ',\n' + \
        'link: "' + link + '",\n' + \
        'year: ' + str(year) + ',\n' + \
        'abstract: "' + abstract + '",\n' + \
        'language: "' + language + '",\n' + \
        'keywords: ' + gen_mutation_string_for_keywords(keywords) + ',\n' + \
        'class: ' + gen_mutation_string_for_classes(classes) + ',\n' + \
        'category: { name: "publications" },\n' + \
        'subtype: { name: "' + subtype + '" }' + \
        'dateUpdate: "' + update_datetime + '"' + \
        """
           }],
            upsert: true) {
                infoObject {
                    title
                    link
                    year
                }
            }    
        }   
        """
    return query_string


async def add_records_to_graphdb_with_updateDate(oaixml, client):
    """
    The add_records_to_graphdb function takes in a chunk of records and adds them to the graphdb database.
    :param oaixml: A chunk of records
    :return: (# of inserted records, # of deleted records)
    """
    
    inserted_records = 0
    deleted_records = 0

    # add chunk of records to the database
    for record in oaixml.find_all('record'):
        # print(record)
        
        # check header if record is deleted ... indicated by tag: status = deleted
        record_deleted = False
        if len(record.header.attrs) > 0:
            if record.header['status'] == 'deleted':
                print('Record is deleted')
                record_deleted = True
                deleted_records += 1

        if not record_deleted:  
            record_dict = gen_record_dict(record)  # extract information for current record

            my_query = gen_pub_mutation_string_update(
                title = record_dict['title'].encode('utf-8').decode('utf-8'),
                authors = record_dict['authors'],
                abstract = record_dict['abstract'].encode('utf-8').decode('utf-8'),
                link = record_dict['link'],
                year = record_dict['year'],
                language = record_dict['language'],
                keywords = record_dict['keywords'],
                classes = record_dict['class'],
                subtype = record_dict['subtype']['name'],
                update_datetime = record_dict['datestamp']  # Note that the time must be in the format of "YYYY-MM-DDTHH:MM:SSZ" and must include the "Z" at the end to indicate that it is in UTC time
                )
            
            # import io
            # with io.open("my_query.gql",'w', encoding='utf-8') as f:
                # f.write(my_query)
        
            query = gql(my_query)
            result = await client.execute_async(query)
            # print(result)
            inserted_records += 1
    return inserted_records, deleted_records


async def run():
    logger.info("run service function")

    limit_batch = settings.LIMIT_BATCH  # -1, no limit ... process all batches

    oai_url = settings.TARGET_HOST  #' https://digitalcollection.zhaw.ch/oai/request/' # url to the oai-pmh api
    graphdb_endpoint = settings.DB_HOST  # 'http://localhost:8080/graphql' # url to the graphdb endpoint
    transport = AIOHTTPTransport(url=graphdb_endpoint) # Select your transport with a defined url endpoint

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # count number of records
    total_inserted_records = 0
    total_deleted_records = 0

    # get_last_dgraph_update_timestamp
    last_update_timestamp = await get_last_dgraph_update_timestamp(client)
    logger.info('Last update timestamp in graphDB: ' + last_update_timestamp)
    last_update_timestamp == None

    # count number of batches to be processed
    batch_count = 0

    # get first chunk of records that have been updated since the last update
    oaixml = get_single_chunk_oai_records_by_date(oai_url, datestamp=last_update_timestamp)
    token = oaixml.resumptionToken

    # add the first chunk of records to the database
    inserted_records, deleted_records = await add_records_to_graphdb_with_updateDate(oaixml, client=client)
    total_inserted_records += inserted_records
    total_deleted_records += deleted_records

    batch_count += 1
    while token is not None:
        if limit_batch > 0 and batch_count < limit_batch: # limit number of batches to be processed   
            # get the next chunk of records
            oaixml = get_single_chunk_oai_records_by_date(oai_url, resumption_token=token)
            token = oaixml.resumptionToken
            # add the next chunk of records to the database
            inserted_records, deleted_records = await add_records_to_graphdb_with_updateDate(oaixml, client=client)
            total_inserted_records += inserted_records
            total_deleted_records += deleted_records
            batch_count += 1
        else:
            token = None
            logging.info('Limit of batches reached. Bacth count: ' + str(batch_count) + ' | Limit: ' + str(limit_batch))

    logger.info('Total number of inserted records: ', total_inserted_records)
    logger.info('finished service function')

# if __name__ == '__main__':
#     await run()
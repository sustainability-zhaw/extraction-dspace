# extraction pipeline for dspace (aka Digital Collection)

## Workflow of the extraction pipeline
`local_dev/get_data_from_digcol_add_to_graphdb.py` 
- script to collect all records from the digital collection and write it in a (local) dgraph DB

The script collect all records from the digital collection with <datestamp> greater/equal than `last_update_timestamp`, in chunks of 100 records. (`get_single_chunk_oai_records_by_date(oai_url, datestamp=last_update_timestamp)`).

First, the `last_update_timestamp` is fetched from the graphDB (`get_last_update_timestamp(client=client)`).

If the `last_update_timestamp` is not set (the graphDB is empty), the script will collect all records older than `1900-01-01T00:00:00Z`, i.e. `get_single_chunk_oai_records_by_date(oai_url, datestamp=None)`

The records are then entered into the dgraph database (`add_records_to_graphdb_with_updateDate(oaixml, client=client)`) whereas `updateDate` of the InfoObject is set to <datestamp> of the OAI recored  

## Harvesting Batch_Size

The common convention for the harvesting batch_size via OAI-PMH is ‘100’ records per request [Open Archives - OAI Flow Control]. If more records are available beyond that first page with batch_size records, a “resumptionToken” is presented. OpenAIRE recommendation is to have a batch_size between 100 and 500 records per request.

### Flow Control (Resumption Tokens)
An OAI data provider can prevent any performance impact caused by harvesting by forcing a harvester to receive data in time-separated chunks. If the data provider receives a request for a lot of data, it can send part of the data with a resumption token. The harvester can then return later with the resumption token and continue.
DSpace supports resumption tokens for "ListRecords", "ListIdentifiers" and "ListSets" OAI-PMH requests.
Each OAI-PMH ListRecords request will return at most 100 records (by default) but it could be configured in the [dspace]/config/crosswalks/oai/xoai.xml file.
When a resumption token is issued, the optional completeListSize and cursor attributes are included. OAI 2.0 resumption tokens are persistent, so expirationDate of the resumption token is undefined, they do not expire.
Resumption tokens contain all the state information required to continue a request and it is encoded in Base64.

## Development

A development environment with dgraph, sample data, and dgraph ratel is provided via `docker-compose-local.yaml`.

To start the environment run the following command: 

```bash
docker compose -f docker-compose-local.yaml up --build --force-recreate db db_init
```

The launch takes approx. 30 seconds. After that period an initialised dgraph database is exposed via `http://localhost:8080/graphql`.

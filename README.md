# extraction pipeline for dspace (aka Digital Collection)

## Workflow of the extraction pipeline
`local_dev/get_data_from_digcol_add_to_graphdb.py` 
- script to collect all records from the digital collection and write it in a (local) dgraph DB

The script collect all records from the digital collection with <datestamp> greater/equal than `last_update_timestamp`, in chunks of 100 records. (`get_single_chunk_oai_records_by_date(oai_url, datestamp=last_update_timestamp)`).

First, the `last_update_timestamp` is fetched from the graphDB (`get_last_update_timestamp(client=client)`).

If the `last_update_timestamp` is not set (the graphDB is empty), the script will collect all records older than `1900-01-01T00:00:00Z`, i.e. `get_single_chunk_oai_records_by_date(oai_url, datestamp=None)`

The records are then entered into the dgraph database (`add_records_to_graphdb_with_updateDate(oaixml, client=client)`) whereas `updateDate` of the InfoObject is set to <datestamp> of the OAI recored  

## Development

A development environment with dgraph, sample data, and dgraph ratel is provided via `docker-compose-local.yaml`.

To start the environment run the following command: 

```bash
docker compose -f docker-compose-local.yaml up --build --force-recreate --remove-orphans
```

The launch takes approx. 30 seconds. After that period an initialised dgraph database is exposed via `localhost:8080`.

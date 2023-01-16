# extraction pipeline for dspace (aka Digital Collection)


`local_dev/get_data_from_digcol_add_to_graphdb.py` 
- script to collect all records from the digital collection and write it in a (local) dgraph DB

- `publication_datestamp` is the date of the last modification of the record in the OAI database in the format `YYYY-MM-DD`
- `dgraph_update_datetime` is the date of the last update of the record in the dgraph database in the format `YYYY-MM-DDTHH:MM:SSZ`

The script collect all records from the digital collection with <datestamp> greater/equal than `publication_datestamp`, in chunks of 100 records. (`get_single_chunk_oai_records_by_date(oai_url, datestamp=publication_datestamp)`)
The records are then entered into the dgraph database (`add_records_to_graphdb_with_updateDate(oaixml, update_datetime=dgraph_update_datetime, client=client)`).




## Development

A development environment with dgraph, sample data, and dgraph ratel is provided via `docker-compose-local.yaml`.

To start the environment run the following command: 

```bash
docker compose -f docker-compose-local.yaml up --build --force-recreate --remove-orphans
```

The launch takes approx. 30 seconds. After that period an initialised dgraph database is exposed via `localhost:8080`.

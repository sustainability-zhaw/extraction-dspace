# extraction pipeline for dspace (aka Digital Collection)


`local_dev/get_data_from_digcol_add_to_graphdb.py` 
- script to collect all records from the digital collection and write it in a (local) dgraph DB

## Development

A development environment with dgraph, sample data, and dgraph ratel is provided via `docker-compose-local.yaml`.

To start the environment run the following command: 

```bash
docker compose -f docker-compose-local.yaml up
```

The launch takes approx. 30 seconds. After that period an initialised dgraph database is exposed via `localhost:8080`.

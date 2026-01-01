#!/bin/bash

set -x

DT=$(date +'%Y-%m-%d')
gsutil rm -r gs://polarize-events/export-$DT || true
gcloud firestore export gs://polarize-events/export-$DT --collection-ids=events

bq load --replace --source_format=DATASTORE_BACKUP polarize_events.events gs://polarize-events/export-$DT/all_namespaces/kind_events/all_namespaces_kind_events.export_metadata

bq extract --destination_format NEWLINE_DELIMITED_JSON 'polarize_events.events' gs://polarize-events/results.json

gcloud storage cp -r gs://polarize-events/results.json results.json

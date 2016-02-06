#!/bin/bash

for x in $1/books*; do
  echo "$x"
  ../../../google_appengine/appcfg.py upload_data --kind=books_book --url=http://egaxegax.appspot.com/_ah/remote_api --config_file=../../../django-egaxegax/bulkloader.yaml --filename="$x"
  sleep 3
done

#!/bin/bash

cd ../../../google_appengine

for x in ../dumps/books/books_book_*$1*; do
  echo "$x"
  ./appcfg.py upload_data --kind=books_book --url=http://egaxegax.appspot.com/_ah/remote_api --config_file=../django-egaxegax/bulkloader.yaml --filename="$x"
  sleep 3
done

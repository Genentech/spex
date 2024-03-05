import demo data from you're container or postgres db
and replate database_dump.sql to you're dump
```
pg_dump -U omero -d omero -W > ~/database_dump.sql
```
default pass omero
when run build.sh, you're database_dump.sql will be import and create container with data
and import it to GitHub packages
```


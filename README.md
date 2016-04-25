# cBioPortal User Management

## Setup

Checkout the source from git

```
git clone ...
cd cbioportal_users
```

Initialize project for Flynn

```
flynn create cbioportalusers-dev
flynn resource add postgres
```

Setup environment

```
flynn env set \
    ALLOWED_HOSTS='*' \
    DJANGO_SETTINGS_MODULE=cbioportal_users.settings.production \
    PORT=80 \
    SECRET_KEY=$(pwgen 100 1)
```

Also, make cBioPortal MySQL database available for cbioportalusers-dev through Flynn Dashboard. Flynn will create environment variable `DATABASE_URL_1` for it. Rename to `DATABASE_URL_CBIOPORTAL`.

Then, push to Flynn

```
git push flynn master
```

Finally, run migrations and create super user

```
flynn run python3 /app/manage.py migrate
flynn run python3 /app/manage.py createsuperuser
```

## Run Locally

You need to have a locally running MySQL database, setup for cBioPortal.

```
DJANGO_SETTINGS_MODULE=cbioportal_users.settings.local DATABASE_URL_CBIOPORTAL=mysql://cbio_user:Eepheiy7@cubi16.bihealth.org:3306/cbioportal python3 manage.py runserver
```

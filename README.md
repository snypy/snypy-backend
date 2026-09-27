[![codebeat badge](https://codebeat.co/badges/636a710b-e6c6-4ca8-ab1b-921bbaa6c816)](https://codebeat.co/projects/github-com-nezhar-snypy-backend-master)
[![codecov](https://codecov.io/gh/snypy/snypy-backend/branch/master/graph/badge.svg?token=FJ8DVxxArd)](https://codecov.io/gh/snypy/snypy-backend)
[![Known Vulnerabilities](https://snyk.io/test/github/nezhar/snypy-backend/badge.svg?targetFile=pyproject.toml)](https://snyk.io/test/github/nezhar/snypy-backend?targetFile=pyproject.toml)

# SnyPy Backend

REST API for managing code snippets build with Django and Django Rest Framework.

## Running the tests

The test suite runs with `pytest` from the `snypy/` directory. The settings are read from
environment variables; the database is configured through `DATABASE_URL`
(see [django-environ](https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url)).

```bash
pip install -e ".[test]"
cd snypy
export DEBUG=True RUN_MODE=test SECRET_KEY=changeme! ALLOWED_HOSTS=localhost,127.0.0.1 \
  CORS_ORIGIN_WHITELIST="http://localhost,http://127.0.0.1" CSRF_TRUSTED_ORIGINS=http://localhost \
  REGISTER_VERIFICATION_URL=http://localhost:4200/verify-user/ \
  RESET_PASSWORD_VERIFICATION_URL=http://localhost:4200/reset-password/ \
  REGISTER_EMAIL_VERIFICATION_URL=http://localhost:4200/verify-email/
export DATABASE_URL=sqlite:////tmp/db.sqlite3
pytest
```

### Testing against PostgreSQL, MariaDB or MySQL

CI runs the suite against SQLite (Python 3.8-3.12) and against PostgreSQL 16, MariaDB 11.4 and
MySQL 8.4 (Python 3.12). The database drivers are optional extras and are not part of the runtime
dependencies:

```bash
pip install -e ".[test,postgres]"   # psycopg
pip install -e ".[test,mysql]"      # mysqlclient, used for both MariaDB and MySQL
```

`mysqlclient` compiles against the MySQL client library; on Debian/Ubuntu install
`default-libmysqlclient-dev` and `pkg-config` first.

The Django test runner creates a separate `test_<name>` database, so the configured user needs
permission to create databases (use `root` for MariaDB/MySQL). Example containers and URLs:

```bash
# PostgreSQL 16
docker run --rm -d -p 5432:5432 -e POSTGRES_USER=snypy -e POSTGRES_PASSWORD=snypy -e POSTGRES_DB=snypy postgres:16
export DATABASE_URL=postgres://snypy:snypy@127.0.0.1:5432/snypy

# MariaDB 11.4
docker run --rm -d -p 3306:3306 -e MARIADB_ROOT_PASSWORD=snypy -e MARIADB_DATABASE=snypy mariadb:11.4
export DATABASE_URL="mysql://root:snypy@127.0.0.1:3306/snypy?charset=utf8mb4"

# MySQL 8.4
docker run --rm -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=snypy -e MYSQL_DATABASE=snypy mysql:8.4
export DATABASE_URL="mysql://root:snypy@127.0.0.1:3306/snypy?charset=utf8mb4"
```

Then run `pytest` from `snypy/` as above.

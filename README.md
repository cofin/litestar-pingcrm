# Ping CRM

A demo application to illustrate how Inertia.js works with Litestar.

![Screenshot of Ping CRM](https://raw.githubusercontent.com/inertiajs/pingcrm/master/screenshot.png)

**Note:** Check out the original [Ping CRM](https://github.com/inertiajs/pingcrm) project for context.

## Installation

Clone the repo locally:

```sh
git clone https://github.com/cofin/litestar-pingcrm.git pingcrm
cd pingcrm
```

Astral's UV is used to managed the development environment.  If you don't have it installed, you can install it with the following command:

```sh
make install-uv
```

Setup configuration:

```sh
cp .env.example .env
```

Next, install the Python and JavaScript dependencies:

```sh
make install
source .venv/bin/activate
pingcrm assets install
```

Run database migrations:

```sh
pingcrm database upgrade
```

Run database seeder:

```sh
pingcrm database load-fixtures
```

Run the Vite & Litestar server for development:

```sh
pingcrm run --debug
```

You're ready to go! Visit Ping CRM in your browser, and login with:

- **Username:** <johndoe@example.com>
- **Password:** secret

## Running tests

To run the Ping CRM tests, run:

```sh
make test
```

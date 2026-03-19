# PaN-Training Ontology Term Redirector

A simple flask based application to compute redirect of ontology term to PaN-Training list of training materials. This is relevant so that [PaNET](https://expands-eu.github.io/ExPaNDS-experimental-techniques-ontology/index-en.html) can include links to PaN-Training from ontology terms. 

## Setup

Installation using [Poetry](https://python-poetry.org/docs/):

```bash
poetry install
```

Start development server:

```bash
poetry run flask --app ontology_term_redirector/main.py run
```

See [term-redirector.service](config/systemd/system/term-redirector.service) for deployment using gunicorn.
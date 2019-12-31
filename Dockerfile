FROM python:3.8

WORKDIR /srv/app

RUN pip install poetry

COPY pyproject.toml poetry.lock /srv/app/

RUN poetry install

COPY . /srv/app/

ENTRYPOINT ["poetry", "run", "python", "data_anonymizer/main.py"]

FROM python:3.11.5

WORKDIR /app
COPY Pipfile Pipfile.lock /app/

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

COPY . /app/

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

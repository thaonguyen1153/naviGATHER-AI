FROM python:3.12-slim

WORKDIR /app

COPY ./app/Pipfile ./app/Pipfile.lock ./

RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

COPY ./app .

EXPOSE 8501 

CMD ["streamlit", "run", "main.py"]
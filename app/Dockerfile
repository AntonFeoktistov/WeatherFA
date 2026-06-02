FROM python:3.12-slim

WORKDIR /workspace

COPY ./app/requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /workspace/app
COPY ./alembic.ini /workspace/alembic.ini
COPY ./alembic /workspace/alembic

ENV PYTHONPATH=/workspace

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
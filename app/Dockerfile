FROM python:3.12-slim

WORKDIR /workspace

COPY ./app/requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /workspace/app
COPY ./alembic.ini /workspace/alembic.ini
COPY ./alembic /workspace/alembic

ENV PYTHONPATH=/workspace

COPY ./app/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
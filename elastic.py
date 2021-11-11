from elasticsearch import AsyncElasticsearch

from app.config import ELASTIC_HOST, ELASTIC_PORT

es = AsyncElasticsearch(
    [f'http://{ELASTIC_HOST}:{ELASTIC_PORT}'], ca_certs=False, verify_certs=False
)

from modules.settings import settings

from peewee import (
    PostgresqlDatabase, Model, CharField, PrimaryKeyField, ForeignKeyField,
    IntegerField
)


db_settings = settings['database']

database = PostgresqlDatabase(db_settings['name'], user=db_settings['user'])
database.connect()


class BaseModel(Model):
    class Meta:
        database = database


class Resource(BaseModel):
    id = PrimaryKeyField()
    uri = CharField(unique=True, max_length=512)


class Endpoint(BaseModel):
    id = PrimaryKeyField()
    url = CharField(unique=True, max_length=512)


class Backlink(BaseModel):
    resource = ForeignKeyField(Resource, related_name='endpoints')
    endpoint = ForeignKeyField(Endpoint, related_name='resources')
    count = IntegerField(default=0)

from enum import unique
from functools import partial
from peewee import *
from database.connection_db import *

db = create_connection_db('plao',
                          'root', 'root', '127.0.0.1', 3306)


class BaseModel(Model):
    class Meta:
        database = db

class Users(BaseModel):
    id_user=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100)
    username = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    creation_date = DateField(formats=None)

    class Meta:
        table_name = 'users'

class Jobs(BaseModel):
    id_job=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    userip = CharField(max_length=100)
    start_date = DateField()
    finish_date = DateField()
    ns_name = CharField(max_length=100)
    fk_user = ForeignKeyField(Users, db_column='id_user')

    class Meta:
        table_name = 'jobs'

class Vnfs(BaseModel):
    id_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')]) 
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()

    class Meta:
        table_name = 'vnfs'

class Clouds(BaseModel):
    id_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    #id_cloud = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    ip = CharField(max_length=100, unique=True)
    external_ip = CharField(max_length=100, unique=True)
    creation_date = DateField()

    class Meta:
        table_name = 'clouds'

class Jobs_Vnfs_Clouds(BaseModel):
    id_jobs_vnf_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    #id_jobs_vnf_cloud = CharField(max_length=100, primary_key=True)
    creation_date = DateField()
    custo = CharField(max_length=100, unique=True)
    fk_job = ForeignKeyField(Jobs, db_column='id_job')
    fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_cloud = ForeignKeyField(Vnfs, db_column='id_cloud')

    class Meta:
        table_name = 'jobs_vnfs_clouds'

class Metrics(BaseModel):
    id_metrica=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100, unique=True)
    fk_cloud = ForeignKeyField(Vnfs, db_column='id_cloud')
    creation_date = DateField()

    class Meta:
        table_name = 'metricas'

class Metrics_Vnfs(BaseModel):
    id_metrica_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateField()
    metric_value = CharField(max_length=100)
    peso = CharField(max_length=100)
    fk_job = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_metrica = ForeignKeyField(Metrics, db_column='id_metrica')

    class Meta:
        table_name = 'metricas_vnfs'

db.create_tables([Users, Jobs, Vnfs, Clouds, Jobs_Vnfs_Clouds, Metrics, Metrics_Vnfs ])
from enum import unique
from functools import partial
from peewee import *
from database.connection_db import *

db = create_connection_db('PLAO',
                          'root', 'root', '127.0.0.1', 3306)


class BaseModel(Model):
    class Meta:
        database = db

class Users(BaseModel):
    id_user = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100)
    username = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    creation_date = DateField(formats=None)

    class Meta:
        table_name = 'users'

class Jobs(BaseModel):
    id_job = AutoField(primary_key=True)
    name = CharField(max_length=100)
    data = CharField(max_length=100)
    userip = CharField(max_length=100)
    start_date = CharField(max_length=100)
    finish_date = CharField(max_length=100)
    ns_name = CharField(max_length=100)
    fk_user = ForeignKeyField(Users, db_column='id_user')
    creation_date = DateField()

    class Meta:
        table_name = 'jobs'

class Vnfs(BaseModel):
    id_vnf = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()
    fk_job = ForeignKeyField(Jobs, db_column='id_job')

    class Meta:
        table_name = 'vnfs'

class Clouds(BaseModel):
    id_cloud = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()

    class Meta:
        table_name = 'clouds'

class Jobs_Vnfs_Clouds(BaseModel):
    id_jobs_vnf_cloud = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()
    fk_job = ForeignKeyField(Jobs, db_column='id_job')
    fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_cloud = ForeignKeyField(Vnfs, db_column='id_cloud')

    class Meta:
        table_name = 'jobs_vnfs_clouds'

class Metricas(BaseModel):
    id_metrica = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()

    class Meta:
        table_name = 'metricas'

class Metricas_Vnfs(BaseModel):
    id_me = BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    id_server_openstack = CharField(max_length=100, unique=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()
    fk_project = CharField(max_length=100)
    state = CharField(max_length=100)
    cookie = CharField(max_length=100)

    class Meta:
        table_name = 'Metricas_Vnfs'

db.create_tables([Users, Jobs, Vnfs, Clouds, Jobs_Vnfs_Clouds, Metricas, Metricas_Vnfs ])
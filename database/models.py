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
        
class Status_Jobs(BaseModel):
    id_status=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateField()
    name = CharField(max_length=100)

    class Meta:
        table_name = 'status_jobs'

class Jobs(BaseModel):
    id_job=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    userip = CharField(max_length=100)
    start_date = DateField()
    finish_date = DateField()
    ns_name = CharField(max_length=100)
    fk_user = ForeignKeyField(Users, db_column='id_user')
    fk_status = ForeignKeyField(Status_Jobs, db_column='id_status')

    class Meta:
        table_name = 'jobs'

class Vnfs(BaseModel):
    id_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')]) 
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()

    class Meta:
        table_name = 'vnfs'


class Degradations_Clouds_Types(BaseModel):
    id_degradation_cloud_type=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100)
    creation_date = DateField()

    class Meta:
        table_name = 'degradations_clouds_types'
        
class Clouds(BaseModel):
    id_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100, unique=True)
    ip = CharField(max_length=100, unique=True)
    external_ip = CharField(max_length=100, unique=True)
    fk_degradation_cloud_type = ForeignKeyField(Degradations_Clouds_Types, db_column='id_degradation_cloud_type')
    threshold_degradation = CharField(max_length=100)
    creation_date = DateField()

    class Meta:
        table_name = 'clouds'


class Jobs_Vnfs_Clouds(BaseModel):
    id_jobs_vnf_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateField()
    cost = CharField(max_length=100)
    fk_job = ForeignKeyField(Jobs, db_column='id_job')
    fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')

    class Meta:
        table_name = 'jobs_vnfs_clouds'

class Degradations_Clouds(BaseModel):
    id_degradation_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    status_degradation_cloud = CharField(max_length=100)
    creation_date = DateField()
    current_value_degradation = CharField(max_length=100)
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')

    class Meta:
        table_name = 'degradations_clouds'

class Metrics(BaseModel):
    id_metric=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100, unique=True)
    fk_cloud = ForeignKeyField(Vnfs, db_column='id_cloud')
    creation_date = DateField()

    class Meta:
        table_name = 'metrics'

class Metrics_Vnfs(BaseModel):
    id_metric_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateField()
    metric_value = CharField(max_length=100)
    weight_percent = CharField(max_length=100)
    fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_metric = ForeignKeyField(Metrics, db_column='id_metric')

    class Meta:
        table_name = 'metrics_vnfs'

db.create_tables([Users, Jobs, Vnfs, Clouds, Jobs_Vnfs_Clouds, Metrics, Metrics_Vnfs, Status_Jobs, Degradations_Clouds_Types, Degradations_Clouds ])
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
    name_user = CharField(max_length=100)
    username_user = CharField(max_length=100, unique=True)
    password_user = CharField(max_length=100)
    token_user = CharField(max_length=100)
    start_token = DateTimeField()
    expiration_token = DateTimeField()
    creation_date_user = DateTimeField()

    class Meta:
        table_name = 'users'
        
class Status(BaseModel):
    id_status=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateTimeField()
    name = CharField(max_length=100)

    class Meta:
        table_name = 'status'

class Jobs(BaseModel):
    id_job=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    userip_job = CharField(max_length=100)
    start_date_job = DateTimeField()
    finish_date_job = DateTimeField()
    nsd_name_job = CharField(max_length=100)
    fk_user = ForeignKeyField(Users, db_column='id_user')
    fk_status = ForeignKeyField(Status, db_column='id_status')

    class Meta:
        table_name = 'jobs'

class Vnfs(BaseModel):
    id_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')]) 
    name = CharField(max_length=100, unique=True)
    creation_date = DateTimeField()

    class Meta:
        table_name = 'vnfs'


class Degradations_Clouds_Types(BaseModel):
    id_degradation_cloud_type=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100)
    creation_date = DateTimeField()

    class Meta:
        table_name = 'degradations_clouds_types'
        
class Clouds(BaseModel):
    id_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100, unique=True)
    ip = CharField(max_length=100, unique=True)
    external_ip = CharField(max_length=100, unique=True)
    vim_id_osm = CharField(max_length=100, unique=True)
    fk_degradation_cloud_type = ForeignKeyField(Degradations_Clouds_Types, db_column='id_degradation_cloud_type') #type degradation configured
    threshold_degradation = CharField(max_length=100) #the threshold value for degradation
    creation_date = DateTimeField()

    class Meta:
        table_name = 'clouds'


class Jobs_Vnfs_Clouds(BaseModel):
    id_jobs_vnf_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateTimeField()
    cost = CharField(max_length=100)
    fk_job = ForeignKeyField(Jobs, db_column='id_job')
    fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')

    class Meta:
        table_name = 'jobs_vnfs_clouds'

class Degradations_Clouds(BaseModel):
    id_degradation_cloud=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    status_degradation_cloud = CharField(max_length=100) #if 1, is degrated, if 0, no degrated
    creation_date = DateTimeField()
    current_value_degradation = CharField(max_length=100)
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')

    class Meta:
        table_name = 'degradations_clouds'

class Metrics(BaseModel):
    id_metric=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100, unique=True )
    creation_date = DateTimeField()

    class Meta:
        table_name = 'metrics'

class Metrics_Clouds(BaseModel):
    id_metric_cloud=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')
    fk_metric = ForeignKeyField(Metrics, db_column='id_metric')
    creation_date = DateTimeField()

    class Meta:
        table_name = 'metrics_clouds'

class Metrics_Vnfs(BaseModel):
    id_metric_vnf=BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    creation_date = DateTimeField()
    metric_value = CharField(max_length=100)
    weight = CharField(max_length=100)
    #fk_vnf = ForeignKeyField(Vnfs, db_column='id_vnf')
    fk_metric = ForeignKeyField(Metrics, db_column='id_metric')
    fk_job_vnf_cloud = ForeignKeyField(Jobs_Vnfs_Clouds, db_column='id_jobs_vnf_cloud')

    class Meta:
        table_name = 'metrics_vnfs'

class Status_NS_Instanciateds(BaseModel):
    id_status_ns_instanciated=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name_osm_status_ns_instanciated = CharField(max_length=100)
    creation_date_status_ns_instanciated = DateTimeField()

    class Meta:
        table_name = 'status_ns_instanciateds'

class NS_Instanciateds(BaseModel):
    id_ns_instanciated=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name_ns_instanciated = CharField(max_length=100)
    id_osm_ns_instanciated = CharField(max_length=100)
    fk_job = ForeignKeyField(Jobs, db_column='id_job')
    fk_status = ForeignKeyField(Status_NS_Instanciateds, db_column='id_status_ns_instanciated')
    creation_date_ns_instanciated = DateTimeField()
    finish_date_ns_instanciated = DateTimeField()

    class Meta:
        table_name = 'ns_instanciateds'

class Status_Vnf_Instanciateds(BaseModel):
    id_status_vnf_instanciated=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name_osm_status_vnf_instanciated = CharField(max_length=100)
    creation_date_status_vnf_instanciated = DateTimeField()

    class Meta:
        table_name = 'status_vnf_instanciateds'

class Vnf_Instanciateds(BaseModel):
    id_vnf_instanciated=BigIntegerField( unique=True, primary_key=True,
            constraints=[SQL('AUTO_INCREMENT')])
    id_osm_vnf_instanciated = CharField(max_length=100)
    name_osm_vnf_instanciated = CharField(max_length=100)
    fk_cloud = ForeignKeyField(Clouds, db_column='id_cloud')
    fk_status = ForeignKeyField(Status, db_column='id_status')
    fk_ns_instanciated = ForeignKeyField(NS_Instanciateds, db_column='id_ns_instanciated')
    creation_date_vnf_instanciated = DateTimeField()
    finish_date_vnf_instanciated = DateTimeField()

    class Meta:
        table_name = 'vnf_instanciateds'

db.create_tables([Users, Jobs, Vnfs, Clouds, Jobs_Vnfs_Clouds, Metrics, Metrics_Vnfs, Status, Degradations_Clouds_Types, Degradations_Clouds, Metrics_Clouds, Status_NS_Instanciateds,NS_Instanciateds, Status_Vnf_Instanciateds,Vnf_Instanciateds ])
from gnocchiclient.exceptions import ResourceTypeNotFound
import shade
from keystoneauth1.identity import v3
from keystoneauth1 import session
#from novaclient import client as nova_client
from gnocchiclient.v1 import client
#from gnocchiclient import auth


VarCloudName='mpes_n1'

# Class to autenticate on OpenStack and return authentication session
class OpenStack_Auth():
    def __init__(self, cloud_name):
        self.cloud = shade.openstack_cloud(cloud=cloud_name)
        # Import credentials witch clouds.yaml
        self.auth_dict = self.cloud.auth
        self.auth = v3.Password(auth_url=str(self.auth_dict['auth_url']),
                                username=str(self.auth_dict['username']),
                                password=str(self.auth_dict['password']),
                                project_name=str(
                                    self.auth_dict['project_name']),
                                user_domain_name=str(
                                    self.auth_dict['user_domain_name']),
                                project_domain_id=str(self.auth_dict['project_domain_id']))
        # Create a session with credentials clouds.yml
        self.sess = session.Session(auth=self.auth, verify=False)

    # Return authentication session
    def get_session(self):
        return self.sess

# Class to get measures from Gnocchi
class Gnocchi():
    def __init__(self, session):
        # param verify : ignore self-signed certificate
        self.gnocchi_client = client.Client(session=session)

    def get_resource_type(self,name):
        try:
            self.gnocchi_client.resource_type.get(name)
            return True
        except ResourceTypeNotFound:
            return False

    def get_resource(self,name):
        try:
            self.gnocchi_client.resource.search(resource_type=name,limit=1)
            return True
        except ResourceTypeNotFound:
            return False

#Class to get servers
class Servers():
    pass


def main():
    #Creating session OpenStack
    auth_session = OpenStack_Auth(cloud_name=VarCloudName)
    sess = auth_session.get_session()

    #Insert Session in Gnocchi object
    gnocchi = Gnocchi(session=sess)

    #Gnocchi(gnocchi.get_metric_cpu_utilization())
    
    if(gnocchi.get_resource_type("plao")==False):
        print("Resource Type plao not exist, creating...")
        #executar metodo para criar novo recurso
    if(gnocchi.get_resource("plao")==False):
        print("Resource plao not exist, creating...")
        #executar metodo para criar novo recurso




    
    #nova = nclient.Client(version='2.1', session=sess)
    #instance = nova.servers.get(OPENSTACK_VM_ID)
    # instance = nova.servers.find(name='vm-replaypcap')
    #flavor = nova.flavors.get(instance.flavor['id'])

    # Get vcpus to calc cpu_util in %
    #OPENSTACK_VM_VCPUS = flavor.vcpus
    # Get VM disk id 
    #ID_DISK = gnocchi.get_resource_disk(OPENSTACK_VM_ID)
    # Get VM Network Interface ID
    #ID_NET_INTERFACE = gnocchi.get_resource_network(OPENSTACK_VM_ID)



if __name__ == "__main__":
    main()
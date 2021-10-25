import subprocess
import yaml

FILE_HYPERVISOR_STATS="C:/Temp/artigo/openstack/hypervisor_stats.yaml"


def LoadFileHypervisorStats(PARAMETER):

    #command_hypervisor1 = subprocess.run(["source" , "admin-openrc.sh"])
    #command_hypervisor2 = subprocess.check_output(["openstack" , "hypervisor", "stats", "show","-f", "yaml"])

    A=open(FILE_HYPERVISOR_STATS, )
    B=yaml.full_load(A)

    current_workload=B['current_workload']
    disk_available_least=B['disk_available_least']
    free_disk_gb=B['free_disk_gb']
    free_ram_mb=B['free_ram_mb']
    local_gb=B['local_gb']
    local_gb_used=B['local_gb_used']
    memory_mb=B['memory_mb']
    memory_mb_used=B['memory_mb_used']
    running_vms=B['running_vms']
    vcpus=B['vcpus']
    vcpus_used=B['vcpus_used']


    print(vcpus_used)

    vcpu_use_percent=(vcpus_used*100)/vcpus
    memory_use_percent=(memory_mb_used*100)/memory_mb
 #   return PARAMETER
    #return (B[PARAMETER])

LoadFileHypervisorStats(vcpus_used)



import configparser
import os
import subprocess
import shlex
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

# vm parameters object for the gcp
class vm_parameters_gcp:
    # init function takes a configuration setting and the section name
    def __init__(self, config: configparser.ConfigParser, sectionName: str) -> None:
        self.purpose = config[sectionName]['purpose']
        self.os = config[sectionName]['os']
        self.name = config[sectionName]['name']
        self.team = config[sectionName]['team']
        self.image = config[sectionName]['image']
        self.zone = config[sectionName]['zone']
        self.image_project = config[sectionName]['imageproject']
        self.project = config[sectionName]['project']

# function to validate the config data and if valid, create a vm_parameters_gcp instance for that section
def getConfigDataGCP(sections, cli_req_gcp, system_req_gcp ) -> bool:
    vm_list = []
    # for each vm which is a section
    for section in sections:
        # check that it is in the correct format
        if(len(cli_req_gcp) + len(system_req_gcp) > len(config[section])):
            print('not enough information in config file')
            return False
        for subsection in config[section]:
            # check all the parameters are valid
            if subsection not in cli_req_gcp and subsection not in system_req_gcp:
                print('extra or invalid parameters in config file')
                return False
        # check the resource group exists or create if doesnt exist
        if not checkName(name=config[section]['name']):
            print('failed because of invalid resource group')
            return False
        # check the image chosen is valid
        if not checkImageGCP(image=config[section]['image']):
            print('failed because image name was not in default image list')
            return False
        # create a vm parameters object, append the vm to the list, and create it
        current_vm = vm_parameters_gcp(config=config, sectionName=section)
        vm_list.append(current_vm)
        create_vm_gcp(current_vm)
    # write to a file
    write_new_file_gcp(vm_list)
    return True

# check the name is valid - must be all lowercase or numbers
def checkName(name: str) -> bool:
    for c in name:
        if c.isupper():
            return False
    return True

# check the image name against the list of images for the gcp command line
def checkImageGCP(image: str) -> bool:
    command = "gcloud compute images list"
    output = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines = True)
    images = output.stdout.split()
    image = image.strip()
    for i in images:
        if i == image:
            return True
    return False

# create the vm for the gcp through the command line
def create_vm_gcp(vm: vm_parameters_gcp):
    command = "gcloud compute instances create " + vm.name + " --image=" + vm.image\
    + " --image-project=" + vm.image_project + " --zone=" + vm.zone
    print(command)
    subprocess.run(shlex.split(command))
    return

# write a new file for the gcp based on the list of vms
def write_new_file_gcp(vm_list: list[vm_parameters_gcp]):
    # get the date and time
    date = datetime.now()
    date_string = date.strftime("%Y-%d-%m:%H:%M:%S")
    new_gcp_filename = 'GCP' + date_string + '.conf'
    # rename the config file
    try:
        os.rename('GCP.conf', new_gcp_filename)
    except:
        print('gcp.conf doesnt exist - you need it to create vms')
        exit(0)

    # write to the vm creation text file
    file = open("VM_creation.txt", "a")
    file.write(date_string)
    try:
        file.write("\nSystem Admin Name: " + os.environ["GCP_USERNAME"])
    except: 
        print('couldnt find username - must set AZURE_USERNAME as env variable')
        file.write("\nSystem Admin Name: Unknown")

    # for each vm, write the vm specific information
    for vm in vm_list:
        file.write("\n\nname: " + vm.name)
        file.write("\nproject: " + vm.project)
        file.write("\npurpose: " + vm.purpose)
        file.write("\nteam: " + vm.team)
        file.write("\nos: " + vm.os)
        file.write("\nstatus: " + get_status_gcp(vm))

# get the status of the vm for the gcp
def get_status_gcp(vm: vm_parameters_gcp) -> str:
    command = "gcloud compute instances list"
    output = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines = True)
    rows = output.stdout.split("\n")
    index = 0
    # get the status by checking each row for the name of the vm
    for r in rows:
        if index == 0:
            index = index + 1
            continue
        columns = r.split()
        if columns[0] == vm.name:
            return columns[-1]
        index = index + 1
    return "vm doesnt exist"

# create a class to store the vm parameters in for azure
class vm_parameters_az:
    # init function takes a configuration setting and the section name
    def __init__(self, config: configparser.ConfigParser, sectionName: str) -> None:
        self.purpose = config[sectionName]['purpose']
        self.os = config[sectionName]['os']
        self.name = config[sectionName]['name']
        self.resource_group = config[sectionName]['resource-group']
        self.team = config[sectionName]['team']
        self.image = config[sectionName]['image']
        self.location = config[sectionName]['location']
        self.admin_username = config[sectionName]['admin-username']
        self.admin_password = config[sectionName]['admin-password']
        self.size = config[sectionName]['size']
        self.disk = config[sectionName]['disk']



# function to validate the config data and if valid, create a vm_parameters_az instance for that section
def getConfigDataAz(sections, cli_req, system_req ) -> bool:
    vmList = []
    for section in sections:
        # for each vm which is a section
        if(len(cli_req) + len(system_req) > len(config[section])):
            print('not enough information in config file')
            return False
        for subsection in config[section]:
            # check all the parameters are valid
            if subsection not in cli_req and subsection not in system_req:
                print('extra or invalid parameters in config file')
                return False
        # check the resource group exists or create if doesnt exist
        if not checkResourceAz(resourceName=config[section]['resource-group'], location=config[section]['location']):
            print('failed because of resource group')
            return False
        # check the image chosen is valid
        if not checkImageAz(config[section]['image']):
            print('failed because image is not in known offline image list')
            return False
        # create a vm parameters object, append the vm to the list, and create it
        current_vm = vm_parameters_az(config=config, sectionName=section)
        vmList.append(current_vm)
        create_vm_az(current_vm)
    write_new_file_az(vm_list=vmList)

    return True

# function checks if the resource group exists for azure
def checkResourceAz(resourceName: str, location: str) -> bool:
    credential = DefaultAzureCredential()
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_client = ResourceManagementClient(credential, subscription_id)
    try:
        resource_list = resource_client.resource_groups.create_or_update(
    resourceName, {"location": "canadacentral"})
        return True
    except Exception as e:
        print(e)
        return False
    
# check that the image in azure exists
def checkImageAz(image: str) -> bool:
    command = "az vm image list"
    output = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines = True)
    images = output.stdout.split()
    for i in images:
        if image == i[1:-2]:
            return True
    return True

# create the vm for azure, taking in vm parameters object
def create_vm_az(vm_parameters_az: vm_parameters_az):
    command = "az vm create --resource-group " + vm_parameters_az.resource_group + " --location " +  vm_parameters_az.location + " --name " \
        + vm_parameters_az.name+ " --image " + vm_parameters_az.image + " --admin-username "+ vm_parameters_az.admin_username+" --admin-password "+ vm_parameters_az.admin_password \
        + " --size " + vm_parameters_az.size + " --data-disk-sizes-gb  " + vm_parameters_az.disk + " --verbose"
    print(command)
    subprocess.run(shlex.split(command))

# get the status of the azure vm
def getStatusAz(vm: vm_parameters_az) -> str:
    command = "az vm get-instance-view --name " + vm.name + " --resource-group " + vm.resource_group \
        + " --query \"instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus\" -o tsv"
    output = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines = True)
    return output.stdout

# write the vms to the file for azure
def write_new_file_az(vm_list: list[vm_parameters_az]):
    # get date and time
    date = datetime.now()
    date_string = date.strftime("%Y-%d-%m:%H:%M:%S")
    new_az_filename = 'azure_' + date_string + '.conf'
    # rename the config file
    try:
        os.rename('azure.conf', new_az_filename)
    except:
        print('azure.conf doesnt exist - you need one to create vms')
        exit(0)

    # write to the vm creation text file
    file = open("VM_creation.txt", "a")
    file.write(date_string)
    try:
        file.write("\nSystem Admin Name: " + os.environ["AZURE_USERNAME"])
    except: 
        print('couldnt find username - must set AZURE_USERNAME as env variable')
        file.write("\nSystem Admin Name: Unknown")

    # write vm specific information for each vm
    for vm in vm_list:
        file.write("\n\nname: " + vm.name)
        file.write("\nproject: " + vm.resource_group)
        file.write("\npurpose: " + vm.purpose)
        file.write("\nteam: " + vm.team)
        file.write("\nos: " + vm.os)
        file.write("\nstatus:" + getStatusAz(vm))

# main to run the program
# creates a configuration file parser
config = configparser.ConfigParser()
try:
    config.read('azure.conf')
except:
    print('no file named azure.conf - please create one')
    exit(0)
# gets sections - which are the names of the different vms you want to create 
sections = config.sections()
#print(sections)
# stores the parameters required for the config file
cli_req = [ 'name', 'resource-group', 'image', 'location', 'admin-username', 'admin-password']
system_req = ['purpose', 'os', 'team', 'size', 'disk']

# calls function for getting data from the config file
success = getConfigDataAz(sections, cli_req, system_req)
success = True
if not success:
    print('exiting now')
    exit(0)
#get date and time

# does the same for gcp
config = configparser.ConfigParser()
try:
    config.read('GCP.conf')
except:
    print('no file named gcp.conf - please create one')
    exit(0)
# gets sections - which are the names of the different vms you want to create 
sections = config.sections()
print(sections)
# stores the parameters required for the config file
cli_req_gcp = ['name', 'imageproject', 'image', 'zone']
system_req_gcp = ['project', 'team', 'purpose', 'os']

getConfigDataGCP(sections, cli_req_gcp, system_req_gcp)
# VM-creation
Creates VMs in GCP and Azure using config files to specify parameters.
This project was for the class cloud computing, CIS4010.

To run this project, you need a file GCP.conf and a file azure.conf.
This is an example of setting up your config file including the necessary parameters. You can have multiple VM's in one file.

# GCP.conf example file:
[gcp01]  
name = linuxserver01  
project = Web Presence Canada  
team = Toronto Office Web Team  
purpose = webserver  
os = linux  
image = debian-10-buster-v20240213  
imageproject = debian-cloud  
zone = northamerica-northeast2-a  
[gcp02]  
name = linuxserver02  
project = Containers Are Us  
team = Toronto Office Container Team  
purpose = containers  
os = linux  
image = ubuntu-pro-1604-xenial-v20240216  
imageproject = ubuntu-os-pro-cloud  
zone = northamerica-northeast2-b  

# azure.conf example file:
[azure01]  
purpose = webserver  
os = linux  
name = linuxServer01  
resource-group = images  
team = Toronto Office Web Grls  
image = Ubuntu2204  
location = canadacentral  
admin-username = azureuser  
admin-password = //  
size = Standard_DS2_v2  
disk = 1  
[azure02]  
purpose = office apps  
os = windows  
name = winServer01  
resource-group = images  
team = Toronto Office Web Guys  
image = Win2022AzureEditionCore  
location = westus3  
admin-username = azureuser  
admin-password = //  
size = Standard_DS2_v2  
disk = 1  

# Setting up AZ
- type 'pip install azure-identity'
- type 'pip install azure-mgmt-resource'
- type 'pip install azure-mgmt-compute'
- ensure to be logged in to the azure terminal
    - if you arent, type az login and then the code wil use your default credentials
  
**Getting the subscription id**
- go to azure portal, click home and subscriotions adnd copuy the subscrpitpon id found in table
- go to terminal and set environment variable AZURE_SUBSCRIPTION_ID- in mac, type export AZURE_SUBSCRIPTION_ID= #enter your id here
- go to terminal and set environment variable AZURE_USERNAME= #enter your username here

**Config file**
- for the azure config file, it needs all the parameters specified in example.conf
- the two extra variables are size and disk - need to specify a size for the sizes and a number for the disks
- it also needs an admin-password and the password must be between 12 and 123 characters in length and must have the 3 of the following: 1 lower case character, 1 upper case character, 1 number and 1 special character


# GCP setup
- download by following these instructions at https://cloud.google.com/sdk/docs/install
- type the command 'gcloud init' and set up
- ensure to set your GCP_USERNAME as an environment variable
- type 'gcloud compute images list' to find a list of available gcloud compute images list - my list was different then her example, ensure to pick one on your list

**Config file**
- for the gcp config file, it needs all the parameters specified in the example conf

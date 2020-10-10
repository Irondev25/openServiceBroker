# Broker for Jenkins enabled Git repository as a service(Conforms to Open Broker Service Specification)

> This project creates a jenkins job and attach it to your github repo using webhooks. So that when push or merge event occur's it will automatically trigger your build.

> This project is proof of concept


## Run Jenkins Enabled GitHub Repository Service Server
```bash
git clone https://github.com/Irondev25/oba.git
python -m virtualenv env
source ./env/bin/activate
cd oba
pip install -r requirements.txt
```

create .env file and paste the following and set correct value of environment variable <br/>

```code
export JENKINS_USERID=jenkinsid
export JENKINS_PASSWORD=jenkinspassword
export JENKINS_URL=http://{jenkinshosturl}/
export WEBHOOK_URL=http://{jenkinshosturl}/github-webhook/
```

and run the following
```bash
python main.py
```
> Server port is defined in main.py (defaults to 5050)

## Using Jenkins Enabled GitHub Repository Service
>Assuming Running on localhost

### 1. Getting Service Catalog
    Method: GET
    Api Endpoint: https://localhost:5050/v2/catalog
    Header: 
        X-Broker-Api-Version: 2.14

### 2. Provision a Service
    Method: PUT
    Api Endpoint: localhost:5050/v2/service_instances/:INSTANCE_ID
    Header:
        X-Broker-Api-Version: 2.14
        Content-Type: application/json
    Parameters: 
        accepts_incomplete: True
    Body:
        {
            "service_id": "Jenkins-Broker",
            "plan_id": "Jenkins-Plan-GID",
            "context": {
                "platform": "localhost-broker",
                "some_field": "local broker system"
            },
            "organization_guid": "irondev25",
            "space_guid": "space-guid-here",
            "parameters": {
                "project_name" : "your_project_name",
                "github_id": "GITHUBID",
                "github_pass": "GITHUBPASSWORD",
                "email": "EMAIL"  #Multiple Email Register, use comma seperated eg. "foo1@mail.com,foo2@mail.com"
            },
            "maintenance_info": {
                "version": "2.1.1+abcdef"
            }
        }

### 3. Deprovision a Service
    Method: DELETE
    Api Endpoint: localhost:5050/v2/service_instances/:INSTANCE_ID
    Header: 
        X-Broker-Api-Version: 2.14
    Parameter: 
        accepts_incomplete: True
        service_id: Jenkins-Broker
        plan_id: Jenkins-Plan-GID

### 4. Get Instance
    Method: GET
    Api Endpoint: http://localhost:5050/v2/service_instances/:INSTANCE_ID
    Header:
        X-Broker-Api-Version: 2.14



>Note: BINDING_ID is redundent for this project but required by OBS Specifications. It can be anything, doesn't matter 

### 5. Instance Binding
    Method: PUT
    Api Endpoint: http://localhost:5050/v2/service_instances/:INSTANCE_ID/service_bindings/:BINDING_ID 
    Headers: 
        X-Broker-Api-Version: 2.14
        Content-Type: application/json
    Parameters: 
        accepts_incomplete: True
    Body:
        {
            "context": {},
            "service_id": "Jenkins-Broker",
            "plan_id": "Jenkins-Plan-GID",
            "bind_resource": {
                "app_guid": "",
                "route": ""
            },
            "parameters": {}
        }

### 6. Delete Binding
    Method: DELETE
    Api Endpoint: http://localhost:5050/v2/service_instances/:INSTANCE_ID/service_bindings/:BINDING_ID
    Headers:
        X-Broker-Api-Version: 2.14
    Parameter: 
        service_id: Jenkins-Broker
        plan_id: Jenkins-Plan-GID


### 7. Get Binding
    Method: PUT
    Api Endpoint: http://localhost:5050/v2/service_instances/jtest/service_bindings/mybinding
    Headers:
        X-Broker-Api-Version: 2.14
    




    

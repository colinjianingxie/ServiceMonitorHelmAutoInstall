# Auto Service Monitor Deployment for Prometheus using Helm Charts

This tutorial will show you how to automatically install service monitor helm charts if a service gets added or deleted. We will be using Minikube to run our kubernetes cluster. 

## Pre-requisites
- Basic knowledge of Kubernetes
- Minikube installed
- Helm installed
- Python 3+ installed

## Step 1: Prometheus
Prometheus is a scraping tool that obtains metrics from various kubernetes objects. 
### Installation:
1. Download the /Prometheus folder from this github repo.
2. Make sure minikube is up and running by typing in the terminal: **minikube start** 
3. Change the terminal directory to the Prometheus folder (**cd into /Prometheus**).
4. Apply all the files by running: 
```
kubectl apply -f prometheus-operator.yaml
kubectl apply -f cluster.yaml
kubectl apply -f prometheus.yaml
kubectl apply -f expose.yaml
```

### Installation Note:
Inside the **Kind: Prometheus** file, notice the **serviceMonitorNamespaceSelector:** and **serviceMonitorSelector:** fields. These two fields will auto detect all namespaces in the kubernetes cluster and auto discover all service monitors within such namespaces.

```
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
spec:
  serviceAccountName: prometheus
  serviceMonitorNamespaceSelector: {} # auto discovers all namespaces
  serviceMonitorSelector: {} # auto discovers all monitors configured one line above
  resources:
    requests:
      memory: 400Mi
  enableAdminAPI: false
```

## Step 2: Helm Install
Helm helps templatize the YAML files needed for the service monitors. We need to install a service monitor for every service within a namespace, so it makes sense to have a single template Service Monitor helm chart that takes in multiple values for the deployments.

### Starting off
1. Inside your terminal, type: **helm init**

### Creating the helm chart
**Note: This repo will contain a mychart template for ease of access.**
1. Inside your terminal, type: **helm create mychart**. This will create a helm chart called "mychart". You can name it whatever you want, but for this tutorial, we will be calling the chart "mychart" for consistency.
2. Navigate to the **/mychart/templates** folder that was created. 
3. Inside the folder, delete every file. We will be putting a general **servicemonitor.yaml** file inside the templates folder as follows:

```
{{ $service_data := .Values.service_monitor.service_data }}
{{ range $service_pair := $service_data }}
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    team: whatever
  name: {{ $service_pair.service_namespace }}-{{ $service_pair.service_name }}-monitor
  namespace: {{ $service_pair.service_namespace }}
spec:
  endpoints:
  - port: {{ $service_pair.port_type }}
  selector:
    matchLabels:
      app: {{ $service_pair.service_name }}
{{ end }}
```

By having only the **servicemonitor.yaml** file inside the templates folder, the helm chart will create the template based off of that one file.
4. We will later be reading off of an overrides file that will fill in the variables, such as ($service_pair.service_name).

### Generating the Overrides file
**Note: Source code for this python script is located inside the repo as well as an example overrides yaml file.**

1. Copy/Paste or Download the **service_monitor_overrides_generator.py** locally:
**Note:** I suggest saving the python file in the same directory as the mychart template.

```python
import os
import yaml
from kubernetes import client, config

#Change if needed
SERVICE_MONITOR_YAML_FILE_NAME = "service_monitor_overrides.yaml"

#WRITING TO THE YAML FILE/UPDATING IT
def write(new_yaml_data_dict):
	sdump = yaml.dump(new_yaml_data_dict,indent=4)

	#the leading spaces and indent=4 are key here!
	with open(SERVICE_MONITOR_YAML_FILE_NAME, "a") as fo:
		fo.write(sdump)

def main():
	#DELETE THE YAML FILE (SO WE CAN OVERWRITE IT)
	if os.path.exists(SERVICE_MONITOR_YAML_FILE_NAME):
		os.remove(SERVICE_MONITOR_YAML_FILE_NAME)

	#CONNECTING TO MINIKUBE
	kube_config = os.getenv('KUBE_CONFIG')
	context = os.getenv('CONTEXT')

	proxy_url = os.getenv('HTTP_PROXY', None)
	config.load_kube_config(config_file=kube_config,
	                        context=context)
	if proxy_url:
	    logging.warning("Setting proxy: {}".format(proxy_url))
	    client.Configuration._default.proxy = proxy_url

	#ACCESSING THE API
	kubernetes_client = client.CoreV1Api()
	v1 = client.CoreV1Api()


	temp_dict = {'service_monitor':{'service_data':{}}}
	generated_dict = []
	# Getting the namespaces:
	for ns in kubernetes_client.list_namespace().items:
		temp_namespace = ns.metadata.name  #Getting specific namespace
		if "test" in temp_namespace: #Change to whatever to filter the namespace, currently filters only namespaces called 'test'
			for svc in kubernetes_client.list_namespaced_service(temp_namespace).items:
				temp_service_name = svc.metadata.name  #Returns the service name
				temp_service_port_type = svc.spec.ports[0].name  #Returns the service port type
				generated_dict.append({'service_namespace':temp_namespace, 'service_name':temp_service_name, 'port_type':temp_service_port_type})

	temp_dict['service_monitor']['service_data'] = generated_dict
	write(temp_dict)
	print("Finished running overrides generator")
	print("File stored as: " + SERVICE_MONITOR_YAML_FILE_NAME)
main()
```
2. Navigate to the **service_monitor_overrides_generator.py** file in your terminal.
3. Run: **kubectl proxy** so the python file can read off of the kubernetes cluster.
4. Run: **python3 service_monitor_overrides_generator.py** to run the python file.
5. Notice the **service_monitor_overrides.yaml** file that's generated.

### How the overrides file connects with the helm template
Here is an example overrides file (assuming you're looking at namespaces with "test" inside the name):

```
service_monitor:
    service_data:
    -   port_type: web
        service_name: example-temp
        service_namespace: test-1234
    -   port_type: web
        service_name: example-temp-2
        service_namespace: test-4321
```

Essentially, there are two services that are being monitored, in the form of: (port type, service name, namespace) - (web, example-temp, test-1234) and (web, example-temp-2, test-4321). 

Helm will read the overrides file and use the template **servicemonitor.yaml** template created and generate the *equivalent* service monitor yaml file:

```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    team: whatever
  name: test-1234-example-temp-monitor
  namespace: test-1234
spec:
  endpoints:
  - port: web
  selector:
    matchLabels:
      app: example-temp
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  labels:
    team: whatever
  name: test-4321-example-temp-2-monitor
  namespace: test-4321
spec:
  endpoints:
  - port: web
  selector:
    matchLabels:
      app: example-temp-2
```

### Deplying the helm chart
Now, we need to officialize the helm chart and deploy it onto the kubernetes cluster.

1. Make sure the **mychart** template is in the same directory as the **service_monitor_overrides_generator.py** and the **service_monitor_overrides.yaml** 
So, the directory should have:
- ../mychart
- ../service_monitor_overrides.yaml
- ../service_monitor_overrides_generator.py

2. 



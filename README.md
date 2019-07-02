# Auto Service Monitor Deployment for Prometheus using Helm Charts

This tutorial will show you how to automatically install service monitor helm charts if a service gets added or deleted. We will be using Minikube to run our kubernetes cluster. 

## Pre-requisites
- Basic knowledge of Kubernetes
- Minikube installed
- Helm installed

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

## Step 2: Helm
Helm helps templatize the YAML files needed for the service monitors. We need to install a service monitor for every service within a namespace, so it makes sense to have a single template Service Monitor helm chart that takes in multiple values for the deployments.

### Starting off
1. Inside your terminal, type: **helm init**

### Creating the helm chart
**Note: This repo will contain a mychart template for ease of access.**
1. Inside your terminal, type: **helm create mychart**. This will create a helm chart called "mychart". You can name it whatever you want, but for this tutorial, we will be calling the chart "mychart" for consistency.
2. Navigate to the **/mychart/templates** folder that was created. 
3. Inside the folder, delete every file. We will be putting a general **servicemonitor.yaml** file inside as follows:

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

4. We will later be reading off of a 

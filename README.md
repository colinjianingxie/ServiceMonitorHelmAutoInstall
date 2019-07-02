# Auto Service Monitor Deployment for Prometheus using Helm Charts

This tutorial will show you how to automatically install service monitor helm charts if a service gets added or deleted. We will be using Minikube to run our kubernetes cluster. 

## Pre-requisites
1. Basic knowledge of Kubernetes
2. Minikube installed

## Prometheus
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

# Automatic Service Monitor installation for Prometheus with Helm Charts

This tutorial will show you how to automatically install service monitor helm charts if a service gets added or deleted.


## Prometheus
Prometheus is a scraping tool that obtains metrics from various kubernetes objects. 
### Installation:



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

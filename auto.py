import os
import time
from kubernetes import client, config

starttime=time.time()
baseTime = 5.0

def get_ns_svc_list(kube_client):
	ns_svc_list = []
	for ns in kube_client.list_namespace().items:
		temp_ns = ns.metadata.name # Returns the namespace
		if "test" in temp_ns:
			for svc in kube_client.list_namespaced_service(temp_ns).items:
				temp_service_name = svc.metadata.name # Returns the service name
				temp_pair = (temp_ns, temp_service_name) # Puts (namespace, service) as tuple
				ns_svc_list.append(temp_pair)
				#NEED TO COMAPRE VS DICTS
	return ns_svc_list
def main():

	print("Starting....")
	print("Current refresh rate is: " + str(baseTime) + "s")
	print(""

		)
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

	# RUN THIS ONCE
	base_service_list = get_ns_svc_list(kubernetes_client)
	while True:
		new_service_list = get_ns_svc_list(kubernetes_client)

		if(new_service_list != base_service_list):
			base_service_list = new_service_list
			print("Running overrides yaml generator")
			os.system("python3 service_monitor_overrides_generator.py")
			print("--------------------------------------------------")
			os.system("helm upgrade testchart mychart -f service_monitor_overrides.yaml")
			print("--------------------------------------------------")
			print("Finished updating helm chart")
		time.sleep(baseTime - ((time.time() - starttime) % baseTime))

main()
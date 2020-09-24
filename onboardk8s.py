import os

cluster_name = input("Your cluster name: ")
namespace = input("namespace: ")
api_key = input("CloudGuard API Key: ")
secret = input("API Secret: ")
cluster_id = input("CloudGuard Cluster ID (From Web Console): ")

print("We are onboarding " + cluster_name + " to CloudGuard")
create_namespace = os.system ('kubectl create namespace %s' % (namespace))
cg_token = os.system('kubectl create secret generic dome9-creds --from-literal=username=%s --from-literal=secret=%s --namespace %s' % (api_key,secret,namespace))
config_map = os.system('kubectl create configmap cp-resource-management-configmap --from-literal=cluster.id=%s --namespace %s' % (cluster_id,namespace))
onboard_1 = os.system('kubectl create serviceaccount cp-resource-management  --namespace %s' % (namespace))
onboard_2 = os.system('kubectl create clusterrole cp-resource-management --verb=get,list --resource=pods,nodes,services,nodes/proxy,networkpolicies.networking.k8s.io,ingresses.extensions,podsecuritypolicies.policy,roles,rolebindings,clusterroles,clusterrolebindings,serviceaccounts,namespaces')
onboard_3 = os.system('kubectl create clusterrolebinding cp-resource-management --clusterrole=cp-resource-management --serviceaccount=checkpoint:cp-resource-management')
onboard_4 = os.system('kubectl create -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace %s' % (namespace))
print(cluster_name + " has been succcessfuly onboarded to CloudGuard")

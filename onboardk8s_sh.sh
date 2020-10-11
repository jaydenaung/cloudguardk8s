#!/bin/bash

# ****************************************************
# CloudGuard CSPM (Dome9) Kubernetes Onboarding Helper
# Author: Jayden Kyaw Htet Aung | Check Point SW Technologies
# See LICENSE and README files
# ****************************************************



read -p "Enter Your Cluster Name: " cluster_name
read -p "Enter Namespace: " namespace
read -p "Enter CloudGuard API Key: " api_key
read -p "Enter CloudGuard API Secret: " secret

dome9ApiUrl="https://api.dome9.com"

CREATION_RESPONSE=$(curl -s -X POST $dome9ApiUrl/v2/KubernetesAccount --header 'Content-Type: application/json' --header 'Accept: application/json' \
-d "{\"name\" : \"$cluster_name\"}" --user $api_key:$secret)
export cluster_id=$(echo $CREATION_RESPONSE | jq -r '.id')
echo "your CloudGuard cluster ID is $cluster_id"

echo "Hello, CloudGuarder! We are onboarding $cluster_name to CloudGuard. Give us a moment."

echo "Creating namespace.."
kubectl create namespace $namespace

echo "Creating CloudGuard Token.."
kubectl create secret generic dome9-creds --from-literal=username=$api_key --from-literal=secret=$secret --namespace $namespace

echo "Configuration map.."
kubectl create configmap cp-resource-management-configmap --from-literal=cluster.id=$cluster_id --namespace $namespace

echo "Finalizing onboarding.."
kubectl create serviceaccount cp-resource-management  --namespace $namespace
kubectl create clusterrole cp-resource-management --verb=get,list --resource=pods,nodes,services,nodes/proxy,networkpolicies.networking.k8s.io,ingresses.extensions,podsecuritypolicies.policy,roles,rolebindings,clusterroles,clusterrolebindings,serviceaccounts,namespaces
kubectl create clusterrolebinding cp-resource-management --clusterrole=cp-resource-management --serviceaccount=checkpoint:cp-resource-management

echo "Deploying CloudGuard agent.."
kubectl create -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace $namespace

echo "Awesome, Cloudguarder! $cluster_name has been succcessfully onboarded to CloudGuard!"

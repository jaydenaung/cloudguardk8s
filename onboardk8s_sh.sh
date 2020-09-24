#!/bin/bash

read -p "Enter Your Cluster Name: " cluster_name
read -p "Enter Namespace: " namespace
read -p "Enter CloudGuard API Key: " api_key
read -p "Enter CloudGuard API Secret: " secret
read -p "Enter Cluster ID (From Cloudguard Web Console): " cluster_id

echo "We are onboarding $cluster_name to CloudGuard."

echo "Creating namespace.."
kubectl create namespace $namespace

echo "Creating CloudGuard Token.."
kubectl create secret generic dome9-creds --from-literal=username=$api_key --from-literal=secret=$secret --namespace $namespace

echo "Configuration map.."
kubectl create configmap cp-resource-management-configmap --from-literal=cluster.id=$cluster_id --namespace $namespace

echo "Finalising onboarding.."
kubectl create serviceaccount cp-resource-management  --namespace $namespace
kubectl create clusterrole cp-resource-management --verb=get,list --resource=pods,nodes,services,nodes/proxy,networkpolicies.networking.k8s.io,ingresses.extensions,podsecuritypolicies.policy,roles,rolebindings,clusterroles,clusterrolebindings,serviceaccounts,namespaces
kubectl create clusterrolebinding cp-resource-management --clusterrole=cp-resource-management --serviceaccount=checkpoint:cp-resource-management

echo "Deploying CloudGuard agent.."
kubectl create -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace $namespace

echo "$cluster_name has been succcessfuly onboarded to CloudGuard!"
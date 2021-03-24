#!/bin/bash

# ****************************************************
# CloudGuard CSPM (Dome9) Kubernetes Onboarding Helper
# Author: Jayden Kyaw Htet Aung | Check Point SW Technologies
# See LICENSE and README files
# ****************************************************

# Update this accordingly
cluster_name="jayden-dev-2"

# Update this accordingly
namespace="checkpoint"

export CHKP_CLOUDGUARD_ID="YOUR-CLOUDGUARD-API-KEY"
export CHKP_CLOUDGUARD_SECRET="YOUR-CLOUDGUARD-API-SECRET"

# If you're using AWS SSM Parameter Stores
#export CHKP_CLOUDGUARD_ID=$(aws ssm get-parameter --name "CHKP_CLOUDGUARD_ID" | jq -r '.Parameter.Value')
#export CHKP_CLOUDGUARD_SECRET=$(aws ssm get-parameter --name "CHKP_CLOUDGUARD_SECRET" | jq -r '.Parameter.Value')

echo "Hello, CloudGuarder! We are removing $cluster_name from CloudGuard. Give us a moment."

echo "Deleting clusterrolebinding.."
kubectl delete clusterrolebinding cp-resource-management --namespace=$namespace

echo "Removing clusterrole .."
kubectl delete clusterrole cp-resource-management

echo "Deleting service account.."
kubectl delete serviceaccount cp-resource-management  --namespace $namespace

echo "Deleting configmap.. "
kubectl delete configmap cp-resource-management-configmap --namespace $namespace

echo "Deleting secret.."
kubectl delete secret dome9-creds --namespace $namespace

echo "Deleting Cloudguard agent.."
kubectl delete -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace $namespace

echo "Finally deleting namespace"
kubectl delete namespace $namespace

echo "Awesome, Cloudguarder! $cluster_name has been succcessfully removed from CloudGuard!"






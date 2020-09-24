#cloudguardk8s

This is a really simple scirpt which automates onboarding your Kubernetes cluster to CloudGuard CSPM (Dome9). The script requires that you already have acces to a CloudGuard CSPM account, have installed kubectl and python 3.x., and obtained CloudGuard API Key and Secret.

Just run the script, and it'll ask for necessary information for you to onboard the cluster. 

If you don't have a CSPM account, register at https://secure.dome9.com/v2 for a free trial account today!
---------------

Note: CloudGuard generates cluster ID for each cluster, and you'll only know the cluster ID when you're at the onboarding wizard (after providing cluster name, namespace, API key/secret, etc.) on the CSPM web console. I'm checking if there is a way to pre-generate it so that the entire process can be automated.

#cloudguardk8s
----------------

This is a really simple scirpt which automates onboarding your Kubernetes cluster to CloudGuard CSPM (Dome9). I've created both Python and Bashshell scripts that basically do the same thing. Either script requires that you already have access to a CloudGuard CSPM account, have installed kubectl and obtained CloudGuard API Key and Secret. Of course Python verstion of the script requires that you've installed Python 3.x. You just need to run either one.

#Python
Just run the script, and it'll ask for necessary information (e.g. cluster name) to onboard the cluster to CloudGuard

For example. "python ./onboardk8s.py"

#Bash shell

Just run the shell script, and it'll ask for necessary information (e.g. cluster name to onboard the cluster to CloudGuard.

For example, "./onboardk8s_sh.sh"

If you don't have a cloudguard CSPM account yet, register at https://secure.dome9.com/v2 for a free trial account today!
---------------

Note: CloudGuard generates cluster ID for each cluster, and you'll only know the cluster ID when you're at the onboarding wizard (after providing cluster name, namespace, API key/secret, etc.) on the CSPM web console. I'm checking if there is a way to pre-generate it so that the entire process can be automated.

import os
import sys
import glob
import requests
import click
import itertools
import yaml
from base64 import b64encode
from jinja2 import Environment, FileSystemLoader

DOME9_API = "https://api.dome9.com/v2/"
ENDPOINTS = { "k8s_account": "KubernetesAccount" }
K8S_JINJA_TPL = 'cloudguard_deployment.j2'

class HiddenPassword(object):
    def __init__(self, password=''):
        self.password = password
    def __str__(self):
        return '*' * len(self.password)

def create_kubernetes_account(api_key: str, secret: str, payload: dict):
    data = dict()
    try:
        print(f'POST {DOME9_API}{ENDPOINTS["k8s_account"]}')
        r = requests.post(f'{DOME9_API}{ENDPOINTS["k8s_account"]}',
                                auth=(api_key, secret),
                                json=payload)
        print(f"Result code: {r.status_code}")
        if r.status_code == 201:
            print("Successfully created K8S cluster in Dome9")
        else:
            print("Could not create K8S cluster in CG Dome9")
            sys.exit(1)
        data = r.json()
    except Exception as e:
        print("Could not create K8S cluster in CG Dome9")
        print(e)
        sys.exit(1)
    return data['id']

def delete_kubernetes_account(api_key: str, secret: str, cluster_id: dict):
    try:
        print(f'DELETE {DOME9_API}{ENDPOINTS["k8s_account"]}/{cluster_id}')
        r = requests.delete(f'{DOME9_API}{ENDPOINTS["k8s_account"]}/{cluster_id}',
                                auth=(api_key, secret))
        print(f"Result code: {r.status_code}")
        if r.status_code == 204:
            print(f"Successful deletion for CG Dome9 K8S cluster {cluster_id}")
        else:
            print(f"Could not remove K8S cluster from CG Dome9")

    except Exception as e:
        print("Could not remove K8S cluster from CG Dome9")
        print(e)
        sys.exit(1)


def render_j2_template(data: dict):
    jinja = Environment(loader = FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    template = jinja.get_template(K8S_JINJA_TPL)
    return template.render(data)

def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

def namespace_from_yaml(yaml_file: str):
    with open(yaml_file, 'r') as f:
        l = []
        for doc in yaml.safe_load_all(f):
            l.append(list(findkeys(doc, 'namespace')))
        flat_list = list(itertools.chain.from_iterable(l))
        if all(x==flat_list[0] for x in flat_list):
            return flat_list[0]
        else:
            # If K8S elements come from different namespaces we don't want to risk
            # removing things from the wrong namespace
            raise Exception("Different namespaces encountered in K8S yaml document")

@click.group()
def cli():
    print("Welcome to Cloud Guard Dome9 K8S onboarding helper")

@cli.command()
@click.option('--cluster-name', '-n', type=str, required=True, prompt='Enter your cluster name')
@click.option('--namespace', '-ns', type=str, required=True, prompt='Enter namespace')
@click.option('--api-key', '-k', type=str,
            prompt='Enter CloudGuard API Key',
            default=lambda: os.environ.get('CHKP_CLOUDGUARD_ID', ''))
@click.option('--secret', '-s', type=str,
            prompt='Enter CloudGuard API Secret',
            hide_input=True,
            default=lambda: HiddenPassword(os.environ.get('CHKP_CLOUDGUARD_SECRET', '')))
def onboard(cluster_name, namespace, api_key, secret):
    """ Onboard a K8S cluster in Cloud Guard Dome9"""
    # Create cluster in Dome9
    cluster_id = create_kubernetes_account(api_key, secret.password, {'name': f"{cluster_name}"})

    # Create Dictionary for Jinja rendering
    j2_data = {
            'namespace': namespace,
            'secret': b64encode(secret.password.encode('ascii')).decode('ascii'),
            'api_key': b64encode(api_key.encode('ascii')).decode('ascii'),
            'cluster_id': cluster_id
            }
    yaml_output = render_j2_template(j2_data)
    # Write the data to a file
    with open(f'{cluster_name}.{cluster_id}.yaml', 'w') as f:
        f.write(yaml_output)

    print(f"Hello CloudGuarder! We are onboarding {cluster_name} with ID: [{cluster_id}] to CloudGuard. Give us a moment")
    create_namespace = os.system (f'kubectl create namespace {namespace}')
    result_cgd9 = os.system(f'kubectl apply -f {cluster_name}.{cluster_id}.yaml')
    result_d9_assets = os.system(f'kubectl create -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace {namespace}')
    print(f'{cluster_name} has been succcessfuly onboarded to CloudGuard!')

@cli.command()
@click.option('--k8s-yaml', '-k',
              required=True,
              prompt='Yaml file generated during onboarding',
              default=lambda: glob.glob('*.yaml')[0],
              help='Yaml file generated during onboarding process')
@click.option('--api-key', '-k', type=str,
            prompt='Enter CloudGuard API Key',
            default=lambda: os.environ.get('CHKP_CLOUDGUARD_ID', ''))
@click.option('--secret', '-s', type=str,
            prompt='Enter CloudGuard API Secret',
            hide_input=True,
            default=lambda: HiddenPassword(os.environ.get('CHKP_CLOUDGUARD_SECRET', '')))
def remove(k8s_yaml, api_key, secret):
    """ Remove a K8S cluster already onboarded in Cloud Guard Dome9"""
    *cluster_name, cluster_id, _ = k8s_yaml.split('.')
    cluster_name = '.'.join(cluster_name)
    print(f"Cluster name: {cluster_name}")
    print(f"Cluster ID: {cluster_id}")
    namespace = namespace_from_yaml(k8s_yaml)
    print("Removing cluster")
    result_cgd9 = os.system(f'kubectl delete -f {k8s_yaml}')
    result_d9_assets = os.system(f'kubectl delete -f https://secure.dome9.com/v2/assets/files/cp-resource-management.yaml --namespace {namespace}')
    delete_kubernetes_account(api_key, secret.password, cluster_id)
    os.remove(k8s_yaml)


if __name__ == '__main__':
    cli()

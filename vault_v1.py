import hvac
import re

from hvac import exceptions
from pprint import pprint

# Global variable for recursive function
secret_list = []
key_list = []
lmp = <password>


def list_mountpoints():
    # Returns a list of all secrets engines
    """compare to: vault secrets list"""
    output = client.sys.list_mounted_secrets_engines()['data']
    return list(output.keys())


def get_all_secrets_v1(mount_point, path):
    # Returns a list of all secrets for a particular v1 path/engine
    try:
        output = client.secrets.kv.v1.list_secrets(
            mount_point=mount_point,
            path=path
        )

        items = output['data']['keys']

        for item in items:
            is_path = re.search('/$', item)
            if is_path:
                # Recursively iterate over path until reaching the secret
                item = path + item
                get_all_secrets_v1(mount_point, item)
            else:
                item = path + item
                secret_list.append(item)

    except exceptions.Forbidden:
        print(mount_point + path, ' NO PERMISSIONS')
        pass

    return secret_list


def get_keys_v1(mount_point, path):
    # Return dictionary of key/value pair secrets
    output = client.secrets.kv.v1.read_secret(
        mount_point=mount_point,
        path=path
    )

    return output['data']


if __name__ == '__main__':

    mount_point = 'kv_core_concourse/'
    path = ''

    url = <url>
    token = <token>
    client = hvac.Client(
        url=url,
        token=token,
    )

    all_secrets_v1 = get_all_secrets_v1(mount_point, path)
    # pprint(all_secrets_v1)

    for secret in all_secrets_v1:
        keys = get_keys_v1(mount_point, secret)
        for key in keys:
            value = keys[key]
            if type(value) == str:
                print('Key: ' + mount_point + secret + '/' + key + ' : ' + value)
            else:
                print(mount_point + secret + '/' + key + ' NOT STRING')
            if value == lmp:
                key_list.append(mount_point + secret + '/' + key)

    print('\nThe following have redundant values for LMP:')
    pprint(key_list)

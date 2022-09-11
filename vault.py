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
        # print(mount_point + path, ' NO PERMISSIONS')
        pass

    return secret_list


def get_all_secrets_v2(mount_point, path):
    # Returns a list of all secrets for a particular V2 path/engine
    try:
        output = client.secrets.kv.v2.list_secrets(
            mount_point=mount_point,
            path=path
        )

        items = output['data']['keys']

        for item in items:
            is_path = re.search('/$', item)
            if is_path:
                # Recursively iterate over path until reaching the secret
                item = path + item
                get_all_secrets_v2(mount_point, item)
            else:
                item = path + item
                secret_list.append(item)

    except exceptions.Forbidden:
        # print(mount_point + path, ' NO PERMISSIONS')
        pass

    return secret_list


def get_keys_v1(mount_point, path):
    # Return dictionary of key/value pair secrets
    output = client.secrets.kv.v1.read_secret(
        mount_point=mount_point,
        path=path
    )

    return output['data']


def get_keys_v2(mount_point, path):
    # Return dictionary of key/value pair secrets
    output = client.secrets.kv.v2.read_secret(
        mount_point=mount_point,
        path=path
    )

    return output['data']['data']


if __name__ == '__main__':

    mount_point_v1 = 'kv_core_concourse/'
    path_v1 = ''
    mount_point_v2 = 'kv_core_secrets/'
    path_v2 = ''

    url = <url>
    token = <token>
    client = hvac.Client(
        url=url,
        token=token,
    )

    all_secrets_v1 = get_all_secrets_v1(mount_point_v1, path_v1)
    print('############ Version 1 ############')
    pprint(all_secrets_v1)

    for secret_v1 in all_secrets_v1:
        keys_v1 = get_keys_v1(mount_point_v1, secret_v1)
        for key_v1 in keys_v1:
            value_v1 = keys_v1[key_v1]
            if type(value_v1) == str:
                print('Key: ' + mount_point_v1 + secret_v1 + '/' + key_v1 + ' : ' + value_v1)
            else:
                print(mount_point_v1 + secret_v1 + '/' + key_v1 + ' NOT STRING')
            if value_v1 == lmp:
                key_list.append(mount_point_v1 + secret_v1 + '/' + key_v1)

    all_secrets_v2 = get_all_secrets_v2(mount_point_v2, path_v2)
    print('############ Version 2 ############')
    pprint(all_secrets_v2)

    for secret_v2 in all_secrets_v2:
        keys_v2 = get_keys_v2(mount_point_v2, secret_v2)
        for key_v2 in keys_v2:
            value_v2 = keys_v2[key_v2]
            if type(value_v2) == str:
                print('Key: ' + mount_point_v2 + secret_v2 + '/' + key_v2 + ' : ' + value_v2)
            else:
                print(mount_point_v2 + secret_v2 + '/' + key_v2 + ' NOT STRING')
            if value_v2 == lmp:
                key_list.append(mount_point_v2 + secret_v2 + '/' + key_v2)

    print('\nThe following have redundant values for LMP:')
    pprint(key_list)

import demistomock as demisto
from CommonServerPython import *  # noqa # pylint: disable=unused-wildcard-import
from CommonServerUserPython import *  # noqa

import requests
import traceback
from typing import Dict, Any
from bs4 import BeautifulSoup

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

''' CONSTANTS '''
POST_HEADERS = {
    'Content-Type': 'application/xml',
    'Accept': 'application/xml'
}

GET_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
MAX_PAGE_SIZE = 1000
''' CLIENT CLASS '''


class Client(BaseClient):

    def get_computers_request(self, computer_id: str = None, basic_subset: bool = False, match: str = None):
        """Retrieve the computers results.
        Args:
            computer_id: The computer id.
            basic_subset: Basic subset for all of the computers.
            match: Match computers by specific characteristics.
        Returns:
            Computers response from API.
        """
        uri = '/computers'
        if computer_id:
            res = self._http_request(method='GET', url_suffix=f'{uri}/id/{computer_id}/subset/General', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        elif basic_subset:
            res = self._http_request(method='GET', url_suffix=f'{uri}/subset/basic', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        elif match:
            res = self._http_request(method='GET', url_suffix=f'{uri}/match/{match}', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        else:
            res = self._http_request(method='GET', url_suffix=uri, headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)

        return res

    def get_computer_subset_request(self, identifier: str, identifier_value: str, subset: str):
        """Retrieve the computer subset results.
        Args:
            identifier: The identifier to search computer.
            identifier_value: The value of the identifier.
            subset: Subset to search for.
        Returns:
            Computer subset response from API.
        """

        url_suffix = f'/computers/{identifier}/{identifier_value}/subset/{subset}'
        res = self._http_request(method='GET', url_suffix=url_suffix, headers=GET_HEADERS,
                                 error_handler=self._generic_error_handler)

        return res

    @staticmethod
    def _generic_error_handler(res):
        if res.status_code == 404:
            err_msg = BeautifulSoup(res.text).body.text
            raise DemistoException(f"The server has not found anything matching the request URI. Origin response from"
                                   f" server: {err_msg}")

    def computer_lock_request(self, computer_id: str, passcode: str, lock_message: str = None):
        """Lock computer.
        Args:
            computer_id: The computer id.
            passcode: The passcode to lock the computer.
            lock_message: The lock message.
        Returns:
            Computer lock response from API.
        """

        uri = '/computercommands/command/DeviceLock'
        request_body = '<?xml version="1.0" encoding="UTF-8"?>' + \
                       '<computer_command>' + \
                       '<general>' + \
                       f'<passcode>{passcode}</passcode>' + \
                       f'<lock_message>{lock_message}</lock_message>' + \
                       '</general>' + \
                       '<computers>' + \
                       '<computer>' + \
                       f'<id>{computer_id}</id>' + \
                       '</computer>' + \
                       '</computers>' + \
                       '</computer_command>'

        res = self._http_request(method='POST', data=request_body, url_suffix=uri, headers=POST_HEADERS,
                                 resp_type='response', error_handler=self._computer_lock_error_handler)

        json_res = json.loads(xml2json(res.content))
        return json_res

    @staticmethod
    def _computer_lock_error_handler(res):
        err_msg = str(BeautifulSoup(res.text).body.text)
        if res.status_code == 400 and 'Unable to match computer' in res.text:
            raise DemistoException(f"ID doesn't exist. Origin error from server: {err_msg}")
        if res.status_code == 400 and 'is not managed' in res.text:
            raise DemistoException(f"Device is unmanaged. Origin error from server: {err_msg}")

    def computer_erase_request(self, computer_id: str, passcode: str):
        """Erase computer.
        Args:
            computer_id: The computer id.
            passcode: The passcode to lock the computer.
        Returns:
            Computer erase response from API.
        """

        uri = '/computercommands/command/EraseDevice'
        request_body = '<?xml version="1.0" encoding="UTF-8"?>' + \
                       '<computer_command>' + \
                       '<general>' + \
                       '<command> EraseDevice </command>' + \
                       f'<passcode>{passcode}</passcode>' + \
                       '</general>' + \
                       '<computers>' + \
                       '<computer>' + \
                       f'<id>{computer_id}</id>' + \
                       '</computer>' + \
                       '</computers>' + \
                       '</computer_command>'

        res = self._http_request(method='POST', data=request_body, url_suffix=uri, headers=POST_HEADERS,
                                 resp_type='response')
        if res.status_code < 200 or res.status_code >= 300:
            return_error('Failed to erase the computer')

        raw_action = json.loads(xml2json(res.content))
        return raw_action

    def get_users_request(self, user_id: str = None, name: str = None, email: str = None):
        """Get users.
        Args:
            user_id: The user id.
            name: The name of the user.
            email: The email of the user.
        Returns:
            Get users response from API.
        """

        uri = '/users'
        if user_id:
            res = self._http_request(method='GET', url_suffix=f'{uri}/id/{id}', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        elif name:
            res = self._http_request(method='GET', url_suffix=f'{uri}/name/{name}', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        elif email:
            res = self._http_request(method='GET', url_suffix=f'{uri}/email/{email}', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)
        else:
            res = self._http_request(method='GET', url_suffix=f'{uri}', headers=GET_HEADERS,
                                     error_handler=self._generic_error_handler)

        return res

    def get_mobile_devices_request(self, mobile_id: str = None, match: str = None):
        """Get mobile devices.
        Args:
            mobile_id: The user id.
            match: Match mobile devices by specific characteristics.
        Returns:
            Get mobile devices response from API.
        """

        uri = '/mobiledevices'
        if mobile_id:
            res = self._http_request(method='GET', url_suffix=f'{uri}/id/{id}', headers=GET_HEADERS)
        elif match:
            res = self._http_request(method='GET', url_suffix=f'{uri}/match/{match}', headers=GET_HEADERS)
        else:
            res = self._http_request(method='GET', url_suffix=f'{uri}', headers=GET_HEADERS)

        return res

    def get_mobile_devices_subset_request(self, identifier: str, identifier_value: str, subset: str):

        """Retrieve the mobile device subset results.
        Args:
            identifier: The identifier to search mobile device.
            identifier_value: The value of the identifier.
            subset: Subset to search for.
        Returns:
            Mobile device subset response from API.
        """

        uri = '/mobiledevices'
        res = self._http_request(method='GET', url_suffix=f'{uri}/{identifier}/{identifier_value}/subset/'
                                                          f'{subset}', headers=GET_HEADERS,
                                 error_handler=self._generic_error_handler)

        return res

    def get_computers_by_app_request(self, app: str, version: str = None):
        """Get computers by application.
        Args:
            app: The name of the application.
            version: The version of the application.
        Returns:
            Get computer by application response from API.
        """

        uri = '/computerapplications'
        if app:
            if version:
                res = self._http_request(method='GET', url_suffix=f'{uri}/application/{app}/version/{version}',
                                         headers=GET_HEADERS)
            else:
                res = self._http_request(method='GET', url_suffix=f'{uri}/application/{app}', headers=GET_HEADERS)
        else:
            err_msg = 'You must specify application argument'
            raise Exception(err_msg)

        return res

    def mobile_device_lost_request(self, mobile_id: str, lost_message: str = None):
        """Lock computer.
        Args:
            mobile_id: The computer id.
            lost_message: The lost message.
        Returns:
            Mobile device lost response from API.
        """

        uri = '/mobiledevicecommands/command/DeviceLock'
        request_body = '<?xml version="1.0" encoding="UTF-8"?>' + \
                       '<mobile_device_command>' + \
                       '<general>' + \
                       '<command>EnableLostMode</command>' + \
                       f'<lost_mode_message>{lost_message}</lost_mode_message>' + \
                       '</general>' + \
                       '<mobile_devices>' + \
                       '<mobile_device>' + \
                       f'<id>{mobile_id}</id>' + \
                       '</mobile_device>' + \
                       '</mobile_devices>' + \
                       '</mobile_device_command>'

        res = self._http_request(method='POST', data=request_body, url_suffix=uri, headers=POST_HEADERS,
                                 resp_type='response')
        if res.status_code < 200 or res.status_code >= 300:
            return_error('Enable Lost Mode failed')

        raw_action = json.loads(xml2json(res.content))
        return raw_action

    def mobile_device_erase_request(self, mobile_id: str = None, preserve_data_plan: bool = False,
                                    clear_activation_code: bool = False):
        """Erase mobile device.
        Args:
            mobile_id: The computer id.
            preserve_data_plan: Retain cellular data plans.
            clear_activation_code: Clear Activation Lock on the device.
        Returns:
           Erase mobile device response from API.
        """

        uri = '/mobiledevicecommands/command/EraseDevice'
        request_body = '<?xml version="1.0" encoding="UTF-8"?>' + \
                       '<mobile_device_command>' + \
                       '<general>' + \
                       '<command>EraseDevice</command>' + \
                       f'<preserve_data_plan>{preserve_data_plan}</preserve_data_plan>' + \
                       f'<clear_activation_code>{clear_activation_code}</clear_activation_code>' + \
                       '</general>' + \
                       '<mobile_devices>' + \
                       '<mobile_device>' + \
                       f'<id>{mobile_id}</id>' + \
                       '</mobile_device>' + \
                       '</mobile_devices>' + \
                       '</mobile_device_command>'

        res = self._http_request(method='POST', data=request_body, url_suffix=uri, headers=POST_HEADERS,
                                 resp_type='response')
        if res.status_code < 200 or res.status_code >= 300:
            return_error('Failed to erase mobile device')

        raw_action = json.loads(xml2json(res.content))
        return raw_action


''' HELPER FUNCTIONS '''


def pagination(response, limit, page):
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE
    return response[page * limit:(page + 1) * limit]


def get_computers_readable_output(computers_response, computer_id=None):
    readable_output = []
    if computer_id:
        readable_output.append({
            'ID': computers_response.get('id'),
            'Name': computers_response.get('name'),
            'MAC Address': computers_response.get('mac_address'),
            'IP Address': computers_response.get('ip_address'),
            'Serial Number': computers_response.get('serial_number'),
            'UDID': computers_response.get('udid'),
            'Jamf Version': computers_response.get('jamf_version'),
            'Platform': computers_response.get('platform'),
        })

    else:
        for computer in computers_response:
            readable_output.append({
                'ID': computer.get('id'),
                'Name': computer.get('name'),

            })
    return readable_output


def get_computer_subset_readable_output(response, subset):
    readable_output = {}
    computers_response = response.get('computer')
    if subset == 'General':
        general_computer_response = computers_response.get('general')
        readable_output = {
            'ID': general_computer_response.get('id'),
            'Name': general_computer_response.get('name'),
            'MAC address': general_computer_response.get('mac_address'),
            'Alternate MAC address': general_computer_response.get('alt_mac_address'),
            'IP address': general_computer_response.get('ip_address'),
            'Serial Number': general_computer_response.get('serial_number'),
            'UDID': general_computer_response.get('udid'),
            'Platform': general_computer_response.get('platform'),
            'Managed': general_computer_response.get('remote_management').get('managed'),
            'Management Username': general_computer_response.get('remote_management').get('management_username')
        }

    elif subset == 'Location':
        location_computer_response = computers_response.get('location')

        readable_output = {
            'Username': location_computer_response.get('username'),
            'Real Name': location_computer_response.get('realname'),
            'Email Address': location_computer_response.get('email_address'),
            'Position': location_computer_response.get('position'),
            'Department': location_computer_response.get('department'),
            'Building': location_computer_response.get('building'),
            'Room': location_computer_response.get('room'),
            'Phone': location_computer_response.get('phone'),

        }
    elif subset == 'Purchasing':
        purchasing_computer_response = computers_response.get('purchasing')

        readable_output = {
            'Is Purchased': purchasing_computer_response.get('is_purchased'),
            'Is Leased': purchasing_computer_response.get('is_leased'),
            'Vendor': purchasing_computer_response.get('vendor'),
            'Purchase Price': purchasing_computer_response.get('purchase_price'),
            'Warranty Expires': purchasing_computer_response.get('warranty_expires'),
            'Lease Expires': purchasing_computer_response.get('lease_expires'),
            'Purchasing Contact': purchasing_computer_response.get('purchasing_contact')
        }

    elif subset == 'Peripherals':
        readable_output = computers_response.get('peripherals')

    elif subset == 'Hardware':
        devices_sizes = []
        for device in computers_response.get('hardware').get('storage'):
            devices_sizes.append({device.get('disk'): device.get('size')})
        readable_output = {
            'Model': computers_response.get('id'),
            'os name': computers_response.get('name'),
            'os version': computers_response.get('mac_address'),
            'os build': computers_response.get('ip_address'),
            'processor type': computers_response.get('id'),
            'number of processors': computers_response.get('name'),
            'number of cores': computers_response.get('mac_address'),
            'total ram': computers_response.get('ip_address'),
            'sip status': computers_response.get('name'),
            'storage': devices_sizes
        }

    elif subset == 'Certificates':
        certificate_details = []
        for certificate in computers_response.get('certificates'):
            certificate_details.append({
                'Common Name': certificate.get('common_name'),
                'Identity': certificate.get('identity'),
                'Expires UTC': certificate.get('expires_utc'),
                'Expires Epoch': certificate.get('expires_epoch')
            })
    elif subset == 'Software':
        readable_output = {
            'Number of running services ': len(computers_response.get('software').get('running_services')),
            'Number of installed applications': len(computers_response.get('software').get('applications')),
        }
    elif subset == 'ExtensionAttributes':
        extension_attributes = []
        for extension_attribute in computers_response.get('extension_attributes'):
            extension_attributes.append({
                'ID': extension_attribute.get('id'),
                'Name': extension_attribute.get('name'),
                'Type': extension_attribute.get('type'),
                'Value': extension_attribute.get('multi_value')
            })
    elif subset == 'GroupsAccounts':
        readable_output = {
            'Number of groups': len(computers_response.get('groups_accounts').get('computer_group_memberships')),
            'Number of installed applications': len(computers_response.get('groups_accounts').get('local_accounts'))
        }
    elif subset == 'iphones':
        readable_output = computers_response.get('iphones')

    elif subset == 'ConfigurationProfiles':
        configuration_profiles = []
        for profile in computers_response.get('configuration_profiles'):
            configuration_profiles.append({
                'ID': profile.get('id'),
                'Is Removable': profile.get('is_removable')
            })

    return readable_output


def computer_commands_readable_output(response):
    computer_response = response.get('computer_command').get('command')
    readable_output = {
        'name': computer_response.get('name'),
        'computer_id': computer_response.get('computer_id'),
        'command_uuid': computer_response.get('command_uuid'),

    }
    return readable_output


def get_users_readable_output(users_response, user_id, name, email):
    readable_output = []
    if user_id or name or email:
        readable_output.append({
            'ID': users_response.get('id'),
            'Name': users_response.get('name'),
            'Email': users_response.get('email'),
            'Phone': users_response.get('phone_number')

        })
    else:
        for user in users_response:
            readable_output.append({
                'ID': user.get('id'),
                'Name': user.get('name'),

            })
    return readable_output


def get_mobile_devices_readable_output(response, mobile_id):
    readable_output = []
    if mobile_id:
        mobile_dev_response = response.get('mobile_device').get('general')
        readable_output.append({
            'ID': mobile_dev_response.get('id'),
            'Name': mobile_dev_response.get('name'),
            'WIFI MAC address': mobile_dev_response.get('wifi_mac_address'),
            'Bluetooth MAC address': mobile_dev_response.get('bluetooth_mac_address'),
            'IP address': mobile_dev_response.get('ip_address'),
            'Serial Number': mobile_dev_response.get('serial_number'),
            'UDID': mobile_dev_response.get('udid'),
            'Model': mobile_dev_response.get('model'),
            'Model Number': mobile_dev_response.get('model_number'),
            'Managed': mobile_dev_response.get('managed'),
            'Supervised': mobile_dev_response.get('supervised')
        })
    else:
        mobile_dev_response = response
        for mobile_device in mobile_dev_response:
            readable_output.append({
                'ID': mobile_device.get('id'),
                'Name': mobile_device.get('name')
            })
    return mobile_dev_response, readable_output


def get_mobile_device_subset_readable_output(response, subset):
    readable_output = {}
    mobile_response = response.get('mobile_device')
    if subset == 'General':
        general_mobile_response = mobile_response.get('general')

        readable_output = {
            'ID': general_mobile_response.get('id'),
            'Name': general_mobile_response.get('name'),
            'WIFI MAC address': general_mobile_response.get('wifi_mac_address'),
            'Bluetooth MAC address': general_mobile_response.get('bluetooth_mac_address'),
            'IP address': general_mobile_response.get('ip_address'),
            'Serial Number': general_mobile_response.get('serial_number'),
            'UDID': general_mobile_response.get('udid'),
            'Model': general_mobile_response.get('model'),
            'Model Number': general_mobile_response.get('model_number'),
            'Managed': general_mobile_response.get('managed'),
            'Supervised': general_mobile_response.get('supervised')
        }
    elif subset == 'Location':
        location_mobile_response = mobile_response.get('location')

        readable_output = {
            'Username': location_mobile_response.get('username'),
            'Real Name': location_mobile_response.get('realname'),
            'Email Address': location_mobile_response.get('email_address'),
            'Position': location_mobile_response.get('position'),
            'Department': location_mobile_response.get('department'),
            'Building': location_mobile_response.get('building'),
            'Room': location_mobile_response.get('room'),
            'Phone': location_mobile_response.get('phone'),

        }
    elif subset == 'Purchasing':
        purchasing_mobile_response = mobile_response.get('purchasing')

        readable_output = {
            'Is Purchased': purchasing_mobile_response.get('is_purchased'),
            'Is Leased': purchasing_mobile_response.get('is_leased'),
            'Vendor': purchasing_mobile_response.get('vendor'),
            'Purchase Price': purchasing_mobile_response.get('purchase_price'),
            'Warranty Expires': purchasing_mobile_response.get('warranty_expires'),
            'Lease Expires': purchasing_mobile_response.get('lease_expires'),
            'Purchasing Contact': purchasing_mobile_response.get('purchasing_contact')
        }
    elif subset == 'Certificates':
        certificates_mobile_response = mobile_response.get('certificates')

        certificate_details = []
        for certificate in certificates_mobile_response:
            certificate_details.append({
                'Common Name': certificate.get('common_name'),
                'Identity': certificate.get('identity'),
                'Expires UTC': certificate.get('expires_utc'),
                'Expires Epoch': certificate.get('expires_epoch')
            })
    elif subset == 'Applications':
        applications_mobile_response = mobile_response.get('applications')

        readable_output = {
            'Number of applications': len(applications_mobile_response)
        }
    elif subset == 'ExtensionAttributes':
        extension_attributes_mobile_response = mobile_response.get('extension_attributes')
        extension_attributes = []
        for extension_attribute in extension_attributes_mobile_response:
            extension_attributes.append({
                'ID': extension_attribute.get('id'),
                'Name': extension_attribute.get('name'),
                'Type': extension_attribute.get('type'),
                'Value': extension_attribute.get('multi_value')
            })
    elif subset == 'ConfigurationProfiles':
        configuration_profiles_mobile_response = mobile_response.get('configuration_profiles')
        configuration_profiles = []
        for profile in configuration_profiles_mobile_response:
            configuration_profiles.append({
                'Display Name': profile.get('display_name'),
                'version': profile.get('version'),
                'identifier': profile.get('identifier'),
                'uuid': profile.get('uuid')
            })
    elif subset == 'Security':
        security_mobile_response = mobile_response.get('security_object')

        readable_output = {
            'Data Protection': security_mobile_response.get('data_protection'),
            'Block Level Encryption Capable': security_mobile_response.get('block_level_encryption_capable'),
            'File Level Encryption Capable': security_mobile_response.get('file_level_encryption_capable'),
            'Passcode Present': security_mobile_response.get('passcode_present'),
            'Passcode Compliant': security_mobile_response.get('passcode_compliant'),
            'Passcode Lock Grace Period Enforced': security_mobile_response.get('passcode_lock_grace_period_enforced'),
            'Hardware Encryption': security_mobile_response.get('hardware_encryption'),
            'Activation Lock Enabled': security_mobile_response.get('activation_lock_enabled'),
            'Jailbreak Detected': security_mobile_response.get('jailbreak_detected'),
            'Lost Mode Enabled': security_mobile_response.get('lost_mode_enabled'),
            'Lost Mode Enforced': security_mobile_response.get('lost_mode_enforced'),
            'Lost Mode Enable Issued UTC': security_mobile_response.get('lost_mode_enable_issued_utc'),
            'Lost Mode Message': security_mobile_response.get('lost_mode_message'),
            'Lost Mode Phone': security_mobile_response.get('lost_mode_phone'),
            'Lost Mode Footnote': security_mobile_response.get('lost_mode_footnote'),
            'Phone': security_mobile_response.get('activation_lock_enabled'),

        }
    elif subset == 'Network':
        network_mobile_response = mobile_response.get('network')

        readable_output = {
            'Home Carrier Network': network_mobile_response.get('home_carrier_network'),
            'Cellular Technology': network_mobile_response.get('cellular_technology'),
            'Voice_roaming_enabled': network_mobile_response.get('voice_roaming_enabled'),
            'Imei': network_mobile_response.get('imei'),
            'Iccid': network_mobile_response.get('iccid'),
            'Meid': network_mobile_response.get('meid'),
            'Current Carrier Network': network_mobile_response.get('current_carrier_network'),
            'Carrier Settings Version': network_mobile_response.get('carrier_settings_version'),
            'Current Mobile Country Code': network_mobile_response.get('current_mobile_country_code'),
            'Current Mobile Network Code': network_mobile_response.get('current_mobile_network_code'),
            'Home Mobile Country Code': network_mobile_response.get('home_mobile_country_code'),
            'Home Mobile Network Code': network_mobile_response.get('home_mobile_network_code'),
            'Data Roaming Enabled': network_mobile_response.get('data_roaming_enabled'),
            'Phone Number': network_mobile_response.get('phone_number')
        }
    elif subset == 'ProvisioningProfiles':
        provisioning_profiles_mobile_response = mobile_response.get('provisioning_profiles')

        readable_output = provisioning_profiles_mobile_response
    elif subset == 'MobileDeviceGroups':
        mobile_device_groups_mobile_response = mobile_response.get('mobile_device_groups')

        readable_output = {
            'Number of groups': len(mobile_device_groups_mobile_response)
        }
    return readable_output


def get_computers_by_app_readable_output(response):
    readable_output = []
    versions_list = response.get('versions')
    for version in versions_list:
        computers_len = len(version.get('computers'))
        readable_output.append({
            'version': version.get('number'),
            'Sum of computers': computers_len
        })

    return readable_output


def mobile_device_commands_readable_output(response):
    mobile_device_response = response.get('mobile_device_command').get('mobile_devices').get('mobile_device')
    readable_output = {
        'ID': mobile_device_response.get('id'),
        'Management ID': mobile_device_response.get('management_id'),

    }
    return mobile_device_response, readable_output


''' COMMAND FUNCTIONS '''


def test_module(client: Client) -> str:
    """Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    :type client: ``Client``
    :param Client: client to use

    :return: 'ok' if test passed, anything else will fail the test.
    :rtype: ``str``
    """

    message: str = ''
    try:
        if client.get_computers_request():
            message = 'ok'
    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):
            message = f'Authorization Error: make sure API Key is correctly set. Original error: {str(e)}'
        else:
            raise e
    return message


def get_computers_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    computer_id = args.get('id')
    basic_subset = argToBoolean(args.get('basic_subset', False))
    match = args.get('match')
    limit = arg_to_number(args.get('limit', 50))
    page = arg_to_number(args.get('page', 0))

    response = client.get_computers_request(computer_id, basic_subset, match)

    if computer_id:
        response = response.get('computer').get('general')
    else:
        response = pagination(response.get('computers'), limit, page)

    readable_output = get_computers_readable_output(response, computer_id)

    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf get computers result',
            readable_output,
            removeNull=True
        ),
        outputs_prefix='JAMF.Computer',
        outputs_key_field='id',
        outputs=response,
        raw_response=response
    )


def get_computer_subset_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    identifier = args['identifier']
    identifier_value = args['identifier_value']
    subset = args['subset']

    response = client.get_computer_subset_request(identifier, identifier_value, subset)
    computer_id = get_computer_id(client, response, subset, identifier, identifier_value)
    readable_output = get_computer_subset_readable_output(response, subset)
    response['computer']['id'] = computer_id
    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf computer subset result',
            readable_output,
            removeNull=True
        ),
        outputs_prefix='JAMF.ComputerSubset.computer',
        outputs_key_field='id',
        outputs=response['computer'],
        raw_response=response
    )


def get_computer_id(client: Client, response, subset, identifier, identifier_value):
    # Need to send another request with General subset to get the computer ID.
    if subset != 'General':
        computer_id = client.get_computer_subset_request(identifier, identifier_value, 'General').\
            get('computer').get('general').get('id')
    else:
        computer_id = response.get('computer').get('general').get('id')
    return computer_id


def computer_lock_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    computer_id = args['id']
    passcode = args['passcode']
    lock_msg = args.get('lock_message')

    response = client.computer_lock_request(computer_id, passcode, lock_msg)
    computer_lock_outputs = computer_commands_readable_output(response)
    return CommandResults(
        readable_output=tableToMarkdown(
            f'Computer {computer_id} locked successfully',
            computer_lock_outputs, removeNull=True, headerTransform=pascalToSpace
        ),
        outputs_prefix='JAMF.ComputeCommands',
        outputs_key_field='id',
        outputs=computer_lock_outputs,
        raw_response=response
    )


def computer_erase_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    computer_id = args['id']
    passcode = args['passcode']

    response = client.computer_erase_request(computer_id, passcode)
    computer_erase_outputs = computer_commands_readable_output(response)
    return CommandResults(
        readable_output=tableToMarkdown(
            f'Computer {computer_id} erase successfully',
            computer_erase_outputs, removeNull=True, headerTransform=pascalToSpace
        ),
        outputs_prefix='JAMF.ComputerCommands',
        outputs_key_field='id',
        outputs=computer_erase_outputs,
        raw_response=response
    )


def get_users_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    user_id = args.get('id')
    name = args.get('name')
    email = args.get('email')
    limit = arg_to_number(args.get('limit', 50))
    page = arg_to_number(args.get('page', 0))

    response = client.get_users_request(user_id, name, email)
    if not user_id and not name and not email:
        response = pagination(response.get('users'), limit, page)
    else:
        response = response['user']
    readable_output = get_users_readable_output(response, user_id, name, email)
    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf get users result',
            readable_output, removeNull=True
        ),
        outputs_prefix='JAMF.User',
        outputs_key_field='id',
        outputs=response,
        raw_response=response
    )


def get_mobile_devices_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    mobile_id = args.get('id')
    match = args.get('match', False)
    limit = arg_to_number(args.get('limit', 50))
    page = arg_to_number(args.get('page', 0))

    response = client.get_mobile_devices_request(mobile_id, match)

    if not mobile_id:
        response = pagination(response.get('mobile_devices'), limit, page)
    computers_response, readable_output = get_mobile_devices_readable_output(response, mobile_id)

    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf get mobile devices result',
            readable_output, removeNull=True
        ),
        outputs_prefix='JAMF.MobileDevice',
        outputs_key_field='id',
        outputs=computers_response,
        raw_response=response
    )


def get_mobile_device_subset_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    identifier = args['identifier']
    identifier_value = args['identifier_value']
    subset = args['subset']

    response = client.get_mobile_devices_subset_request(identifier, identifier_value, subset)
    if subset != 'General':
        mobile_id = client.get_mobile_devices_subset_request(identifier, identifier_value, 'General')\
            .get('mobile_device').get('general').get('id')
    else:
        mobile_id = response.get('mobile_device').get('general').get('id')

    readable_output = get_mobile_device_subset_readable_output(response, subset)
    response['mobile_device']['id'] = mobile_id
    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf mobile device subset result',
            readable_output,
            removeNull=True
        ),
        outputs_prefix='JAMF.MobileDeviceSubset.mobiledevice',
        outputs_key_field='id',
        outputs=response['mobile_device'],
        raw_response=response
    )


def get_computers_by_app_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    app = args['application']
    version = args.get('version')
    limit = arg_to_number(args.get('limit', 50))
    page = arg_to_number(args.get('page', 0))
    response = client.get_computers_by_app_request(app, version)

    computers_list = pagination(response.get('computer_applications').get('unique_computers'), limit, page)

    readable_output = get_computers_by_app_readable_output(response.get('computer_applications'))[:limit]
    outputs = {'application': app, 'computers': computers_list}
    return CommandResults(
        readable_output=tableToMarkdown(
            'Jamf computers by application result',
            readable_output, removeNull=True
        ),
        outputs_prefix='JAMF.ComputersByApp',
        outputs_key_field='application',
        outputs=outputs,
        raw_response=response
    )


def mobile_device_lost_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    mobile_id = args['id']
    lost_mode_msg = args.get('lost_mode_message')

    response = client.mobile_device_lost_request(mobile_id, lost_mode_msg)
    outputs, readable_output = mobile_device_commands_readable_output(response)
    outputs['name'] = 'EnableLostMode'

    return CommandResults(
        readable_output=tableToMarkdown(
            f'Computer {mobile_id} locked successfully',
            readable_output, removeNull=True
        ),
        outputs_prefix='JAMF.MobileDeviceCommands',
        outputs_key_field='id',
        outputs=outputs,
        raw_response=response
    )


def mobile_device_erase_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    mobile_id = args['id']
    preserve_data_plan = args.get('preserve_data_plan', False)
    clear_activation_code = args.get('clear_activation_code', False)
    response = client.mobile_device_erase_request(mobile_id, preserve_data_plan, clear_activation_code)
    outputs, readable_output = mobile_device_commands_readable_output(response)
    outputs['name'] = 'EraseDevice'
    return CommandResults(
        readable_output=tableToMarkdown(
            f'Mobile device {mobile_id} erased successfully',
            readable_output, removeNull=True
        ),
        outputs_prefix='JAMF.MobileDeviceCommands',
        outputs_key_field='id',
        outputs=outputs,
        raw_response=response
    )


''' MAIN FUNCTION '''


def main() -> None:

    try:
        params = demisto.params()
        base_url = urljoin(params.get('url', '').rstrip('/'), '/JSSResource')
        username = params.get('credentials', {}).get('identifier')
        password = params.get('credentials', {}).get('password')

        verify_certificate = not params.get('insecure', False)
        proxy = params.get('proxy', False)

        client = Client(base_url=base_url, verify=verify_certificate, proxy=proxy, auth=(username, password))

        if demisto.command() == 'test-module':
            result = test_module(client)
            return_results(result)

        elif demisto.command() == 'jamf-computers-get':
            return_results(get_computers_command(client, demisto.args()))

        elif demisto.command() == 'jamf-get-computer-subset':
            return_results(get_computer_subset_command(client, demisto.args()))

        elif demisto.command() == 'jamf-computer-lock':
            return_results(computer_lock_command(client, demisto.args()))

        elif demisto.command() == 'jamf-computer-erase':
            return_results(computer_erase_command(client, demisto.args()))

        elif demisto.command() == 'jamf-get-users':
            return_results(get_users_command(client, demisto.args()))

        elif demisto.command() == 'jamf-get-mobile-devices':
            return_results(get_mobile_devices_command(client, demisto.args()))

        elif demisto.command() == 'jamf-get-mobile-device-subset':
            return_results(get_mobile_device_subset_command(client, demisto.args()))

        elif demisto.command() == 'jamf-get-computers-by-application':
            return_results(get_computers_by_app_command(client, demisto.args()))

        elif demisto.command() == 'jamf-mobile-device-lost-mode':
            return_results(mobile_device_lost_command(client, demisto.args()))

        elif demisto.command() == 'jamf-mobile-device-erase':
            return_results(mobile_device_erase_command(client, demisto.args()))
    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()

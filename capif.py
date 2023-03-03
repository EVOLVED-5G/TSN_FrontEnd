from evolved5g.sdk import CAPIFProviderConnector
from os.path import exists, join, dirname, abspath
from random import choice
from string import ascii_letters
from requests.exceptions import RequestException
from typing import Dict


def maybePublishApi(config: Dict):
    detailsFile = './capif_data/publisherDetails.txt'

    if exists(detailsFile):  # Publish the API through CAPIF only once
        print("API already registered.")
    else:
        baseFolder = abspath(join(dirname(__file__), 'capif_data'))
        user = "tsn_" + ''.join(choice(ascii_letters) for _ in range(6))
        password = ''.join(choice(ascii_letters) for _ in range(6))

        host = config['FrontEnd']['Host']
        port = config['FrontEnd']['Port']
        capif = config['CAPIF']

        with open(join(baseFolder, 'tsn_af_api.Template'), 'r', encoding='utf-8') as template:
            with open(join(baseFolder, 'tsn_af_api.json'), 'w', encoding='utf-8') as output:
                for line in template:
                    output.write(line
                                 .replace('<<HOST>>', f'"{host}"')
                                 .replace('<<PORT>>', str(port)))

        capif_connector = CAPIFProviderConnector(certificates_folder=baseFolder,
                                                 capif_host=capif['Host'],
                                                 capif_http_port=capif['HttpPort'],
                                                 capif_https_port=capif['HttpsPort'],
                                                 capif_netapp_username=user,
                                                 capif_netapp_password=password,
                                                 description="TSN AF API",
                                                 csr_common_name="tsnAfExposer",
                                                 csr_organizational_unit="test_app_ou",
                                                 csr_organization="test_app_o",
                                                 crs_locality="Madrid",
                                                 csr_state_or_province_name="Madrid",
                                                 csr_country_name="ES",
                                                 csr_email_address="test@example.com"
                                                 )
        try:
            capif_connector.register_and_onboard_provider()

            capif_connector.publish_services(
                service_api_description_json_full_path=abspath(join(baseFolder, 'tsn_af_api.json')))

            with open(detailsFile, 'w', encoding="utf-8") as output:
                output.write(f'API registered with the following details:\n')
                output.write(f'  User: {user}\n')
                output.write(f'  Password: {password}\n')
                output.write(f'  Host: {host}\n')
                output.write(f'  Port: {port}\n')

            print("API registered in CAPIF")
        except RequestException as e:
            print(f'Unable to publish API. Exception: {e}')


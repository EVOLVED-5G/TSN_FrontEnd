from evolved5g.sdk import CAPIFProviderConnector
from os.path import exists, join, dirname, abspath
from random import choice
from string import ascii_letters
from requests.exceptions import RequestException
from typing import Dict

class CapifHandler:
    detailsFile = './capif_data/publisherDetails.txt'
    baseFolder = abspath(join(dirname(__file__), 'capif_data'))

    def __init__(self, config: Dict):
        self.frontEndHost = config['FrontEnd']['Host']
        self.frontEndPort = config['FrontEnd']['Port']

        capif = config['CAPIF']
        self.host = capif['Host']
        self.httpPort = capif['HttpPort']
        self.httpsPort = capif['HttpsPort']
        self.securityEnabled = capif['SecurityEnabled']
        self.loggingEnabled = capif['LoggingEnabled']

    def MaybePublishApi(self) -> [None | str]:
        if exists(self.detailsFile):  # Publish the API through CAPIF only once
            print("API already registered.")
        else:
            user = "tsn_" + ''.join(choice(ascii_letters) for _ in range(6))
            password = ''.join(choice(ascii_letters) for _ in range(6))

            with open(join(self.baseFolder, 'tsn_af_api.Template'), 'r', encoding='utf-8') as template:
                with open(join(self.baseFolder, 'tsn_af_api.json'), 'w', encoding='utf-8') as output:
                    for line in template:
                        output.write(line
                                     .replace('<<HOST>>', f'"{self.frontEndHost}"')
                                     .replace('<<PORT>>', str(self.frontEndPort)))

            capif_connector = CAPIFProviderConnector(certificates_folder=self.baseFolder,
                                                     capif_host=self.host,
                                                     capif_http_port=self.httpPort,
                                                     capif_https_port=self.httpsPort,
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
                    service_api_description_json_full_path=abspath(join(self.baseFolder, 'tsn_af_api.json')))

                with open(self.detailsFile, 'w', encoding="utf-8") as output:
                    output.write(f'API registered with the following details:\n')
                    output.write(f'  User: {user}\n')
                    output.write(f'  Password: {password}\n')
                    output.write(f'  Host: {self.frontEndHost}\n')
                    output.write(f'  Port: {self.frontEndPort}\n')

                print("API registered in CAPIF")
            except RequestException as e:
                print(f'Unable to publish API. Exception: {e}')

        if self.securityEnabled:
            certPath = join(self.baseFolder, 'capif_cert_server.pem')
            if not exists(certPath):
                print("Certificate file not found")
                return None
            else:
                with open(certPath, 'rb') as certFile:
                    certificate = certFile.read()

                from OpenSSL import crypto
                crypt = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
                publicKey = crypt.get_pubkey()
                return crypto.dump_publickey(crypto.FILETYPE_PEM, publicKey)
        else:
            print("Security is disabled.")
            return None

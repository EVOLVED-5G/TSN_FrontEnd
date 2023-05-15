from evolved5g.sdk import CAPIFProviderConnector, CAPIFLogger
from os.path import exists, join, dirname, abspath
from random import choice
from string import ascii_letters
from requests.exceptions import RequestException
from typing import Dict

class CapifHandler:
    detailsFile = './capif_data/publisherDetails.txt'
    baseFolder = abspath(join(dirname(__file__), 'capif_data'))

    initialized = False
    frontEndHost = frontEndPort = None
    host = httpPort = httpsPort = None
    securityEnabled = loggingEnabled = None

    capifLogger = apiId = None

    @classmethod
    def Initialize(cls, config: Dict):
        cls.frontEndHost = config['FrontEnd']['Host']
        cls.frontEndPort = config['FrontEnd']['Port']

        capif = config['CAPIF']
        cls.host = capif['Host']
        cls.httpPort = capif['HttpPort']
        cls.httpsPort = capif['HttpsPort']
        cls.securityEnabled = capif['SecurityEnabled']
        cls.loggingEnabled = capif['LoggingEnabled']

        cls.initialized = True

    @classmethod
    def MaybePublishApi(cls) -> [None | str]:
        if not cls.initialized:
            raise RuntimeError("CapifHandler must be initialized before calling this method.")

        if exists(cls.detailsFile):  # Publish the API through CAPIF only once
            print("API already registered.")
        else:
            user = "tsn_" + ''.join(choice(ascii_letters) for _ in range(6))
            password = ''.join(choice(ascii_letters) for _ in range(6))

            with open(join(cls.baseFolder, 'tsn_af_api.Template'), 'r', encoding='utf-8') as template:
                with open(join(cls.baseFolder, 'tsn_af_api.json'), 'w', encoding='utf-8') as output:
                    for line in template:
                        output.write(line
                                     .replace('<<HOST>>', f'"{cls.frontEndHost}"')
                                     .replace('<<PORT>>', str(cls.frontEndPort)))

            capif_connector = CAPIFProviderConnector(certificates_folder=cls.baseFolder,
                                                     capif_host=cls.host,
                                                     capif_http_port=cls.httpPort,
                                                     capif_https_port=cls.httpsPort,
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
                    service_api_description_json_full_path=abspath(join(cls.baseFolder, 'tsn_af_api.json')))

                with open(cls.detailsFile, 'w', encoding="utf-8") as output:
                    output.write(f'API registered with the following details:\n')
                    output.write(f'  User: {user}\n')
                    output.write(f'  Password: {password}\n')
                    output.write(f'  Host: {cls.frontEndHost}\n')
                    output.write(f'  Port: {cls.frontEndPort}\n')

                print("API registered in CAPIF")
            except RequestException as e:
                print(f'Unable to publish API. Exception: {e}')

        if cls.securityEnabled:
            certPath = join(cls.baseFolder, 'capif_cert_server.pem')
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

    @classmethod
    def MaybeLog(cls, invokerId, resource, uri, method, time, payload, response, code):
        if not cls.initialized:
            raise RuntimeError("CapifHandler must be initialized before calling this method.")

        if cls.loggingEnabled:
            if cls.apiId is None:
                try:
                    cls.capifLogger = CAPIFLogger(certificates_folder=cls.baseFolder,
                                                  capif_host=cls.host, capif_https_port=str(cls.httpsPort))
                    serviceDescription = cls.capifLogger.get_capif_service_description(
                        capif_service_api_description_json_full_path=join(cls.baseFolder, "CAPIF_tsn_af_api.json"))
                    cls.apiId = serviceDescription["apiId"]
                except Exception as e:
                    print(f"Unable to retrieve apiId: '{e}'")

            entry = cls.capifLogger.LogEntry(
                apiId=cls.apiId, apiVersion='v1', apiName='/tsn/api/',
                resourceName=resource, uri=uri, protocol='HTTP_1_1',
                invocationTime=time, invocationLatency=10, operation=method,
                result=str(code), inputParameters=payload, outputParameters=response
            )

            try:
                cls.capifLogger.save_log(invokerId, [entry])
            except Exception as e:
                with open("error.log", "a") as err:
                    err.write(f"Unable to send log to CAPIF: '{e}'\n")
                    err.write(f"Entry: {entry}\n\n")


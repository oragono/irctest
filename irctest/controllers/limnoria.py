import os
import subprocess
from typing import Optional, Type

from irctest import authentication, tls
from irctest.basecontrollers import BaseClientController, DirectoryBasedController

TEMPLATE_CONFIG = """
supybot.directories.conf: {directory}/conf
supybot.directories.data: {directory}/data
supybot.directories.migrations: {directory}/migrations
supybot.log.level: DEBUG
supybot.log.stdout.level: {loglevel}

supybot.networks: testnet
supybot.networks.testnet.servers: {hostname}:{port}

supybot.protocols.ssl.verifyCertificates: True
supybot.networks.testnet.ssl: {enable_tls}
supybot.networks.testnet.ssl.serverFingerprints: {trusted_fingerprints}

supybot.networks.testnet.sasl.username: {username}
supybot.networks.testnet.sasl.password: {password}
supybot.networks.testnet.sasl.ecdsa_key: {directory}/ecdsa_key.pem
supybot.networks.testnet.sasl.mechanisms: {mechanisms}
"""


class LimnoriaController(BaseClientController, DirectoryBasedController):
    software_name = "Limnoria"
    supported_sasl_mechanisms = {
        "PLAIN",
        "ECDSA-NIST256P-CHALLENGE",
        "SCRAM-SHA-256",
        "EXTERNAL",
    }
    supports_sts = True

    def create_config(self) -> None:
        super().create_config()
        with self.open_file("bot.conf"):
            pass
        with self.open_file("conf/users.conf"):
            pass

    def run(
        self,
        hostname: str,
        port: int,
        auth: Optional[authentication.Authentication],
        tls_config: Optional[tls.TlsConfig] = None,
    ) -> None:
        if tls_config is None:
            tls_config = tls.TlsConfig(enable=False, trusted_fingerprints=[])
        # Runs a client with the config given as arguments
        assert self.proc is None
        self.create_config()
        if auth:
            mechanisms = " ".join(mech.to_string() for mech in auth.mechanisms)
            if auth.ecdsa_key:
                with self.open_file("ecdsa_key.pem") as fd:
                    fd.write(auth.ecdsa_key)
        else:
            mechanisms = ""
        with self.open_file("bot.conf") as fd:
            fd.write(
                TEMPLATE_CONFIG.format(
                    directory=self.directory,
                    loglevel="CRITICAL",
                    hostname=hostname,
                    port=port,
                    username=auth.username if auth else "",
                    password=auth.password if auth else "",
                    mechanisms=mechanisms.lower(),
                    enable_tls=tls_config.enable if tls_config else "False",
                    trusted_fingerprints=" ".join(tls_config.trusted_fingerprints)
                    if tls_config
                    else "",
                )
            )
        assert self.directory
        self.proc = subprocess.Popen(
            ["supybot", os.path.join(self.directory, "bot.conf")]
        )


def get_irctest_controller_class() -> Type[LimnoriaController]:
    return LimnoriaController

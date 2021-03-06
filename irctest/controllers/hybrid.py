import os
import subprocess
from typing import Optional, Set, Type

from irctest.basecontrollers import (
    BaseServerController,
    DirectoryBasedController,
    NotImplementedByController,
)

TEMPLATE_CONFIG = """
serverinfo {{
    name = "My.Little.Server";
    sid = "42X";
    description = "test server";
{ssl_config}
}};
listen {{
    host = "{hostname}";
    port = {port};
}};
general {{
    disable_auth = yes;
    anti_nick_flood = no;
    max_nick_changes = 256;
    throttle_count = 512;
}};
auth {{
    user = "*";
    flags = exceed_limit;
    {password_field}
}};
"""

TEMPLATE_SSL_CONFIG = """
    rsa_private_key_file = "{key_path}";
    ssl_certificate_file = "{pem_path}";
    ssl_dh_param_file = "{dh_path}";
"""


class HybridController(BaseServerController, DirectoryBasedController):
    software_name = "Hybrid"
    supports_sts = False
    supported_sasl_mechanisms: Set[str] = set()

    def create_config(self) -> None:
        super().create_config()
        with self.open_file("server.conf"):
            pass

    def run(
        self,
        hostname: str,
        port: int,
        *,
        password: Optional[str],
        ssl: bool,
        valid_metadata_keys: Optional[Set[str]] = None,
        invalid_metadata_keys: Optional[Set[str]] = None,
    ) -> None:
        if valid_metadata_keys or invalid_metadata_keys:
            raise NotImplementedByController(
                "Defining valid and invalid METADATA keys."
            )
        assert self.proc is None
        self.create_config()
        self.port = port
        password_field = 'password = "{}";'.format(password) if password else ""
        if ssl:
            self.gen_ssl()
            ssl_config = TEMPLATE_SSL_CONFIG.format(
                key_path=self.key_path, pem_path=self.pem_path, dh_path=self.dh_path
            )
        else:
            ssl_config = ""
        with self.open_file("server.conf") as fd:
            fd.write(
                TEMPLATE_CONFIG.format(
                    hostname=hostname,
                    port=port,
                    password_field=password_field,
                    ssl_config=ssl_config,
                )
            )
        assert self.directory
        self.proc = subprocess.Popen(
            [
                "ircd",
                "-foreground",
                "-configfile",
                os.path.join(self.directory, "server.conf"),
                "-pidfile",
                os.path.join(self.directory, "server.pid"),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def get_irctest_controller_class() -> Type[HybridController]:
    return HybridController

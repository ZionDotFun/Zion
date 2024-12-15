import logging

import base58
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore

logger = logging.getLogger(__name__)

keypair = Keypair()

public_key = keypair.pubkey()
logger.info("Public Key:", public_key)

secret_key = keypair.secret()
secret_key_base58 = base58.b58encode(secret_key)
logger.info("Secret Key(Base58):", secret_key_base58.decode("utf-8"))
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

keypair = Keypair()

public_key = keypair.pubkey()
print("Public Key:", public_key)

secret_key = keypair.secret()
secret_key_base58 = base58.b58encode(secret_key)
print("Secret Key(Base58):", secret_key_base58.decode("utf-8"))
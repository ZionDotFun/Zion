from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from base58 import b58decode

class SolanaAgentKit:
    """
    Main class for interacting with Solana blockchain
    Provides a unified interface for token operations, NFT management, and trading

    Attributes:
        connection (AsyncClient): Solana RPC connection
        wallet (Keypair): Wallet keypair for signing transactions
        wallet_address (PublicKey): Public key of the wallet
        openai_api_key (str): API key for OpenAI
    """

    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com", openai_api_key: str = ""):
        self.connection = AsyncClient(rpc_url)
        self.wallet = Keypair.from_secret_key(b58decode(private_key))
        self.wallet_address = self.wallet.public_key
        self.openai_api_key = openai_api_key

    async def close_connection(self):
        """
        Closes the Solana RPC connection.
        """
        await self.connection.close()

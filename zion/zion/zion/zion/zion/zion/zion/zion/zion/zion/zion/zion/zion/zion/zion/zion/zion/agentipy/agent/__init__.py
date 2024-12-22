import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import PublicKey

from agentipy.constants import DEFAULT_OPTIONS
from agentipy.tools import (deploy_token, get_balance, get_tps,
                            launch_pumpfun_token, lend, request_faucet_funds,
                            stake_with_jup, trade, transfer)
from agentipy.types import PumpfunTokenOptions


class SolanaAgentKit:
    """
    Main class for interacting with Solana blockchain.
    Provides a unified interface for token operations, NFT management, and trading.

    Attributes:
        connection (AsyncClient): Solana RPC connection.
        wallet (Keypair): Wallet keypair for signing transactions.
        wallet_address (PublicKey): Public key of the wallet.
        openai_api_key (str): OpenAI API key for additional functionality.
    """

    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com", openai_api_key: str = ""):
        self.connection = AsyncClient(rpc_url)
        self.wallet = Keypair.from_secret_key(base58.b58decode(private_key))
        self.wallet_address = self.wallet.public_key
        self.openai_api_key = openai_api_key

    async def request_faucet_funds(self):
        return await request_faucet_funds(self)

    async def deploy_token(self, decimals: int = DEFAULT_OPTIONS["TOKEN_DECIMALS"]):
        return await deploy_token(self, decimals)

    async def get_balance(self, token_address: PublicKey = None):
        return await get_balance(self, token_address)

    async def transfer(self, to: PublicKey, amount: int, mint: PublicKey = None):
        return await transfer(self, to, amount, mint)

    async def trade(self, output_mint: PublicKey, input_amount: int, input_mint: PublicKey = None, slippage_bps: int = DEFAULT_OPTIONS["SLIPPAGE_BPS"]):
        return await trade(self, output_mint, input_amount, input_mint, slippage_bps)

    async def lend_assets(self, amount: int):
        return await lend(self, amount)

    async def get_tps(self):
        return await get_tps(self)

    async def launch_pump_fun_token(self, token_name: str, token_ticker: str, description: str, image_url: str, options: PumpfunTokenOptions = None):
        return await launch_pumpfun_token(self, token_name, token_ticker, description, image_url, options)

    async def stake(self, amount: int):
        return await stake_with_jup(self, amount)

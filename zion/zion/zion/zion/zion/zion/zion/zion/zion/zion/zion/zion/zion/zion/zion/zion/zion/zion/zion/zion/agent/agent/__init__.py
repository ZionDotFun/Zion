import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore

from agentipy.constants import DEFAULT_OPTIONS
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
        self.wallet = Keypair.from_base58_string(private_key)
        self.wallet_address = self.wallet.pubkey()
        self.openai_api_key = openai_api_key

    async def request_faucet_funds(self):
        from agentipy.tools.request_faucet_funds import FaucetManager
        return await FaucetManager.request_faucet_funds(self)

    async def deploy_token(self, decimals: int = DEFAULT_OPTIONS["TOKEN_DECIMALS"]):
        from agentipy.tools.deploy_token import TokenDeploymentManager
        return await TokenDeploymentManager.deploy_token(self, decimals)

    async def get_balance(self, token_address: Pubkey = None):
        from agentipy.tools.get_balance import BalanceFetcher
        return await BalanceFetcher.get_balance(self, token_address)
    
    async def fetch_price( token_id: str):
        from agentipy.tools.fetch_price import TokenPriceFetcher
        return await TokenPriceFetcher.fetch_price(token_id)

    async def transfer(self, to: Pubkey, amount: int, mint: Pubkey = None):
        from agentipy.tools.transfer import TokenTransferManager
        return await TokenTransferManager.execute_transfer(self, to, amount, mint)

    async def trade(self, output_mint: Pubkey, input_amount: int, input_mint: Pubkey = None, slippage_bps: int = DEFAULT_OPTIONS["SLIPPAGE_BPS"]):
        from agentipy.tools.trade import TradeManager
        return await TradeManager.trade(self, output_mint, input_amount, input_mint, slippage_bps)

    async def lend_assets(self, amount: int):
        from agentipy.tools.lend import AssetLender
        return await AssetLender.lend(self, amount)

    async def get_tps(self):
        from agentipy.tools.get_tps import SolanaPerformanceTracker
        return await SolanaPerformanceTracker.fetch_current_tps(self)
    
    async def get_token_data_by_ticker(ticker:str):
        from agentipy.tools.get_token_data import TokenDataManager
        return await TokenDataManager.get_token_data_by_ticker(ticker)
    
    async def get_token_data_by_address(mint:str):
        from agentipy.tools.get_token_data import TokenDataManager
        return await TokenDataManager.get_token_data_by_address(Pubkey.from_string(mint))

    async def launch_pump_fun_token(self, token_name: str, token_ticker: str, description: str, image_url: str, options: PumpfunTokenOptions = None):
        from agentipy.tools.launch_pumpfun_token import PumpfunTokenManager
        return await PumpfunTokenManager.launch_pumpfun_token(self, token_name, token_ticker, description, image_url, options)

    async def stake(self, amount: int):
        from agentipy.tools.stake_with_jup import StakeManager
        return await StakeManager.stake_with_jup(self, amount)

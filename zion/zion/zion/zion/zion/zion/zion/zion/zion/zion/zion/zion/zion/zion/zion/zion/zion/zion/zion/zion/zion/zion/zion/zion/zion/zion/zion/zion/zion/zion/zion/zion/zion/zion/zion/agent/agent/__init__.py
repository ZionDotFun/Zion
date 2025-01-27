from typing import Optional

import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore

from agentipy.constants import DEFAULT_OPTIONS
from agentipy.types import PumpfunTokenOptions
from agentipy.utils.meteora_dlmm.types import ActivationType


class SolanaAgentKit:
    """
    Main class for interacting with Solana blockchain.
    Provides a unified interface for token operations, NFT management, and trading.

    Attributes:
        connection (AsyncClient): Solana RPC connection.
        wallet (Keypair): Wallet keypair for signing transactions.
        wallet_address (Pubkey): Public key of the wallet.
        openai_api_key (str): OpenAI API key for additional functionality.
    """

    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com", openai_api_key: str = ""):
        self.connection = AsyncClient(rpc_url)
        self.wallet = Keypair.from_base58_string(private_key)
        self.wallet_address = self.wallet.pubkey()
        self.openai_api_key = openai_api_key
        self.rpc_url = rpc_url

    async def request_faucet_funds(self):
        from agentipy.tools.request_faucet_funds import FaucetManager
        return await FaucetManager.request_faucet_funds(self)

    async def deploy_token(self, decimals: int = DEFAULT_OPTIONS["TOKEN_DECIMALS"]):
        from agentipy.tools.deploy_token import TokenDeploymentManager
        return await TokenDeploymentManager.deploy_token(self, decimals)

    async def get_balance(self, token_address: Optional[Pubkey] = None):
        from agentipy.tools.get_balance import BalanceFetcher
        return await BalanceFetcher.get_balance(self, token_address)
    
    async def fetch_price(self, token_id: str):
        from agentipy.tools.fetch_price import TokenPriceFetcher
        return await TokenPriceFetcher.fetch_price(token_id)

    async def transfer(self, to: Pubkey, amount: int, mint: Optional[Pubkey] = None):
        from agentipy.tools.transfer import TokenTransferManager
        return await TokenTransferManager.execute_transfer(self, to, amount, mint)

    async def trade(self, output_mint: Pubkey, input_amount: int, input_mint: Optional[Pubkey] = None, slippage_bps: int = DEFAULT_OPTIONS["SLIPPAGE_BPS"]):
        from agentipy.tools.trade import TradeManager
        return await TradeManager.trade(self, output_mint, input_amount, input_mint, slippage_bps)

    async def lend_assets(self, amount: int):
        from agentipy.tools.lend import AssetLender
        return await AssetLender.lend(self, amount)

    async def get_tps(self):
        from agentipy.tools.get_tps import SolanaPerformanceTracker
        return await SolanaPerformanceTracker.fetch_current_tps(self)
    
    async def get_token_data_by_ticker(self, ticker: str):
        from agentipy.tools.get_token_data import TokenDataManager
        return TokenDataManager.get_token_data_by_ticker(ticker)
    
    async def get_token_data_by_address(self, mint: str):
        from agentipy.tools.get_token_data import TokenDataManager
        return TokenDataManager.get_token_data_by_address(Pubkey.from_string(mint))

    async def launch_pump_fun_token(self, token_name: str, token_ticker: str, description: str, image_url: str, options: Optional[PumpfunTokenOptions] = None):
        from agentipy.tools.launch_pumpfun_token import PumpfunTokenManager
        return await PumpfunTokenManager.launch_pumpfun_token(self, token_name, token_ticker, description, image_url, options)

    async def stake(self, amount: int):
        from agentipy.tools.stake_with_jup import StakeManager
        return await StakeManager.stake_with_jup(self, amount)
    
    async def create_meteora_dlmm_pool(self, bin_step: int, token_a_mint: Pubkey, token_b_mint: Pubkey, initial_price: float, price_rounding_up: bool, fee_bps: int, activation_type: ActivationType, has_alpha_vault: bool, activation_point: Optional[int]):
        from agentipy.tools.create_meteora_dlmm_pool import MeteoraManager
        return await MeteoraManager.create_meteora_dlmm_pool(self, bin_step, token_a_mint, token_b_mint, initial_price, price_rounding_up, fee_bps, activation_type, has_alpha_vault, activation_point)
    
    async def buy_with_raydium(self, pair_address: str, sol_in: float = 0.01, slippage: int = 5):
        from agentipy.tools.use_raydium import RaydiumManager
        return await RaydiumManager.buy_with_raydium(self, pair_address, sol_in, slippage)
    
    async def sell_with_raydium(self, pair_address: str, percentage: int = 100, slippage: int = 5):
        from agentipy.tools.use_raydium import RaydiumManager
        return await RaydiumManager.sell_with_raydium(self, pair_address, percentage, slippage)
    
    async def burn_and_close_accounts(self, token_account: str):
        from agentipy.tools.burn_and_close_account import BurnManager
        return await BurnManager.burn_and_close_account(self, token_account)
    
    async def multiple_burn_and_close_accounts(self, token_accounts: list[str]):
        from agentipy.tools.burn_and_close_account import BurnManager
        return await BurnManager.process_multiple_accounts(self, token_accounts)
    
    async def create_gibwork_task(self, title: str, content: str, requirements: str, tags: list[str], token_mint_address: Pubkey, token_amount: int):
        from agentipy.tools.create_gibwork import GibworkManager
        return await GibworkManager.create_gibwork_task(self, title, content, requirements, tags, token_mint_address, token_amount)
    
    async def buy_using_moonshot(self, mint_str: str, collateral_amount: float = 0.01, slippage_bps: int = 500):
        from agentipy.tools.use_moonshot import MoonshotManager
        return await MoonshotManager.buy(self, mint_str, collateral_amount, slippage_bps)
    
    async def sell_using_moonshot(self, mint_str: str, token_balance: float = 0.01, slippage_bps: int = 500):
        from agentipy.tools.use_moonshot import MoonshotManager
        return await MoonshotManager.sell(self, mint_str, token_balance, slippage_bps)
    
    async def pythFetchPrice(self, mint_str: str):
        from agentipy.tools.use_pyth import PythManager
        return await PythManager.get_price(mint_str)

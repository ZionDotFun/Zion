from typing import List, Optional

import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore

from agentipy.constants import DEFAULT_OPTIONS
from agentipy.types import PumpfunTokenOptions
from agentipy.utils.meteora_dlmm.types import ActivationType


class SolanaAgentKitError(Exception):
    """Custom exception for errors in SolanaAgentKit"""
    pass


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

    def __init__(self, private_key: str, rpc_url: str = "https://api.mainnet-beta.solana.com", openai_api_key: str = "", helius_api_key: str = "", helius_rpc_url: str = ""):
        self.connection = AsyncClient(rpc_url)
        self.wallet = Keypair.from_base58_string(private_key)
        self.wallet_address = self.wallet.pubkey()
        self.openai_api_key = openai_api_key
        self.rpc_url = rpc_url
        self.helius_api_key = helius_api_key
        self.helius_rpc_url = helius_rpc_url

    async def request_faucet_funds(self):
        from agentipy.tools.request_faucet_funds import FaucetManager
        try:
            return await FaucetManager.request_faucet_funds(self)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to request faucet funds: {e}")

    async def deploy_token(self, decimals: int = DEFAULT_OPTIONS["TOKEN_DECIMALS"]):
        from agentipy.tools.deploy_token import TokenDeploymentManager
        try:
            return await TokenDeploymentManager.deploy_token(self, decimals)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to deploy token: {e}")

    async def get_balance(self, token_address: Optional[Pubkey] = None):
        from agentipy.tools.get_balance import BalanceFetcher
        try:
            return await BalanceFetcher.get_balance(self, token_address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to fetch balance: {e}")
    
    async def fetch_price(self, token_id: str):
        from agentipy.tools.fetch_price import TokenPriceFetcher
        try:
            return await TokenPriceFetcher.fetch_price(token_id)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to fetch price: {e}")

    async def transfer(self, to: str, amount: int, mint: Optional[Pubkey] = None):
        from agentipy.tools.transfer import TokenTransferManager
        try:
            return await TokenTransferManager.transfer(self, to, amount, mint)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to execute transfer: {e}")

    async def trade(self, output_mint: Pubkey, input_amount: int, input_mint: Optional[Pubkey] = None, slippage_bps: int = DEFAULT_OPTIONS["SLIPPAGE_BPS"]):
        from agentipy.tools.trade import TradeManager
        try:
            return await TradeManager.trade(self, output_mint, input_amount, input_mint, slippage_bps)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to trade: {e}")

    async def lend_assets(self, amount: int):
        from agentipy.tools.lend import AssetLender
        try:
            return await AssetLender.lend_asset(self, amount)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to lend asset: {e}")

    async def get_tps(self):
        from agentipy.tools.get_tps import SolanaPerformanceTracker
        try:
            return await SolanaPerformanceTracker.fetch_current_tps(self)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to fetch tps: {e}")
    
    async def get_token_data_by_ticker(self, ticker: str):
        from agentipy.tools.get_token_data import TokenDataManager
        try:
            return TokenDataManager.get_token_data_by_ticker(ticker)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to get token data: {e}")
    
    async def get_token_data_by_address(self, mint: str):
        from agentipy.tools.get_token_data import TokenDataManager
        try: 
            return TokenDataManager.get_token_data_by_address(Pubkey.from_string(mint))
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to get token data: {e}")

    async def launch_pump_fun_token(self, token_name: str, token_ticker: str, description: str, image_url: str, options: Optional[PumpfunTokenOptions] = None):
        from agentipy.tools.launch_pumpfun_token import PumpfunTokenManager
        try:
            return await PumpfunTokenManager.launch_pumpfun_token(self, token_name, token_ticker, description, image_url, options)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to launch token on pumpfun: {e}")

    async def stake(self, amount: int):
        from agentipy.tools.stake_with_jup import StakeManager
        try:
            return await StakeManager.stake_with_jup(self, amount)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to stake: {e}")
    
    async def create_meteora_dlmm_pool(self, bin_step: int, token_a_mint: Pubkey, token_b_mint: Pubkey, initial_price: float, price_rounding_up: bool, fee_bps: int, activation_type: ActivationType, has_alpha_vault: bool, activation_point: Optional[int]):
        from agentipy.tools.create_meteora_dlmm_pool import MeteoraManager
        try:
            return await MeteoraManager.create_meteora_dlmm_pool(self, bin_step, token_a_mint, token_b_mint, initial_price, price_rounding_up, fee_bps, activation_type, has_alpha_vault, activation_point)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to create dlmm pool: {e}")
    
    async def buy_with_raydium(self, pair_address: str, sol_in: float = 0.01, slippage: int = 5):
        from agentipy.tools.use_raydium import RaydiumManager
        try:
            return await RaydiumManager.buy_with_raydium(self, pair_address, sol_in, slippage)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to buy using raydium: {e}")
    
    async def sell_with_raydium(self, pair_address: str, percentage: int = 100, slippage: int = 5):
        from agentipy.tools.use_raydium import RaydiumManager
        try:
            return await RaydiumManager.sell_with_raydium(self, pair_address, percentage, slippage)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to sell using raydium: {e}")
    
    async def burn_and_close_accounts(self, token_account: str):
        from agentipy.tools.burn_and_close_account import BurnManager
        try:
            return await BurnManager.burn_and_close_account(self, token_account)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to close account: {e}")
    
    async def multiple_burn_and_close_accounts(self, token_accounts: list[str]):
        from agentipy.tools.burn_and_close_account import BurnManager
        try:
            return await BurnManager.process_multiple_accounts(self, token_accounts)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to close accounts: {e}")
    
    async def create_gibwork_task(self, title: str, content: str, requirements: str, tags: list[str], token_mint_address: Pubkey, token_amount: int):
        from agentipy.tools.create_gibwork import GibworkManager
        try:
            return await GibworkManager.create_gibwork_task(self, title, content, requirements, tags, token_mint_address, token_amount)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to create task: {e}")
    
    async def buy_using_moonshot(self, mint_str: str, collateral_amount: float = 0.01, slippage_bps: int = 500):
        from agentipy.tools.use_moonshot import MoonshotManager
        try:
            return await MoonshotManager.buy(self, mint_str, collateral_amount, slippage_bps)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to buy using moonshot: {e}")
    
    async def sell_using_moonshot(self, mint_str: str, token_balance: float = 0.01, slippage_bps: int = 500):
        from agentipy.tools.use_moonshot import MoonshotManager
        try:
            return await MoonshotManager.sell(self, mint_str, token_balance, slippage_bps)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to sell using moonshot: {e}")
    
    async def pyth_fetch_price(self, mint_str: str):
        from agentipy.tools.use_pyth import PythManager
        try:
            return await PythManager.get_price(mint_str)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_balances(self, address: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_balances(self, address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def get_address_name(self, address: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_address_name(self, address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_nft_events(self, accounts: List[str],
            types: List[str] = None,
            sources: List[str] = None,
            start_slot: int = None,
            end_slot: int = None,
            start_time: int = None,
            end_time: int = None,
            first_verified_creator: List[str] = None,
            verified_collection_address: List[str] = None,
            limit : int = None,
            sort_order: str = None,
            pagination_token: str = None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_nft_events(self, accounts,types,sources,start_slot,end_slot,start_time,end_time,first_verified_creator,verified_collection_address,limit,sort_order,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_mintlists(self, first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        limit: int=None,
        pagination_token: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_mintlists(self,first_verified_creators,verified_collection_addresses,limit,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_nft_fingerprint(self, mints: List[str]):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_nft_fingerprint(self,mints)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_active_listings(self, first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        marketplaces: List[str]=None,
        limit: int=None,
        pagination_token: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_active_listings(self,first_verified_creators,verified_collection_addresses,marketplaces,limit,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_nft_metadata(self, mint_accounts: List[str]):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_nft_metadata(self,mint_accounts)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_raw_transactions(self,
        accounts: List[str], 
        start_slot: int=None,
        end_slot: int=None,
        start_time: int=None,
        end_time: int=None,
        limit: int=None,
        sort_order: str=None,
        pagination_token: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_raw_transactions(self,accounts,start_slot,end_slot,start_time,end_time,limit,sort_order,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_parsed_transactions(self, transactions: List[str], commitment: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_parsed_transactions(self,transactions,commitment)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
    
    async def get_parsed_transaction_history(self,
        address: str, 
        before: str='', 
        until: str='', 
        commitment: str='',
        source: str='',
        type: str=''):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_parsed_transaction_history(self,address,before,until,commitment,source,type)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def create_webhook(self, 
        webhook_url: str, 
        transaction_types: list, 
        account_addresses: list, 
        webhook_type: str, 
        txn_status: str="all",
        auth_header: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.create_webhook(self,webhook_url,transaction_types,account_addresses,webhook_type,txn_status,auth_header)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_all_webhooks(self):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_all_webhooks(self)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_webhook(self, webhook_id: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.get_webhook(self,webhook_id)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def edit_webhook(self,
        webhook_id: str, 
        webhook_url: str, 
        transaction_types: list, 
        account_addresses: list, 
        webhook_type: str, 
        txn_status: str="all",
        auth_header: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.edit_webhook(self,webhook_id,webhook_url,transaction_types,account_addresses,webhook_type,txn_status,auth_header)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def delete_webhook(self, webhook_id: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return await HeliusManager.delete_webhook(self,webhook_id)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

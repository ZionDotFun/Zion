import os
from typing import List, Optional

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore

from agentipy.constants import BASE_PROXY_URL, DEFAULT_OPTIONS
from agentipy.types import BondingCurveState, PumpfunTokenOptions
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

    def __init__(
        self,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        helius_api_key: Optional[str] = None,
        helius_rpc_url: Optional[str] = None,
        quicknode_rpc_url: Optional[str] = None
    ):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.wallet = Keypair.from_base58_string(private_key or os.getenv("SOLANA_PRIVATE_KEY", ""))
        self.wallet_address = self.wallet.pubkey()
        self.private_key = private_key or os.getenv("SOLANA_PRIVATE_KEY", "")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.helius_api_key = helius_api_key or os.getenv("HELIUS_API_KEY", "")
        self.helius_rpc_url = helius_rpc_url or os.getenv("HELIUS_RPC_URL", "")
        self.quicknode_rpc_url = quicknode_rpc_url or os.getenv("QUICKNODE_RPC_URL", "")
        self.base_proxy_url = BASE_PROXY_URL

        self.connection = AsyncClient(self.rpc_url)

        if not self.wallet or not self.wallet_address:
            raise SolanaAgentKitError("A valid private key must be provided.")

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

    async def transfer(self, to: str, amount: float, mint: Optional[Pubkey] = None):
        from agentipy.tools.transfer import TokenTransferManager
        try:
            return await TokenTransferManager.transfer(self, to, amount, mint)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to execute transfer: {e}")

    async def trade(self, output_mint: Pubkey, input_amount: float, input_mint: Optional[Pubkey] = None, slippage_bps: int = DEFAULT_OPTIONS["SLIPPAGE_BPS"]):
        from agentipy.tools.trade import TradeManager
        try:
            return await TradeManager.trade(self, output_mint, input_amount, input_mint, slippage_bps)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to trade: {e}")

    async def lend_assets(self, amount: float):
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
            return HeliusManager.get_balances(self, address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def get_address_name(self, address: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_address_name(self, address)
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
            return HeliusManager.get_nft_events(self, accounts,types,sources,start_slot,end_slot,start_time,end_time,first_verified_creator,verified_collection_address,limit,sort_order,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_mintlists(self, first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        limit: int=None,
        pagination_token: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_mintlists(self,first_verified_creators,verified_collection_addresses,limit,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_nft_fingerprint(self, mints: List[str]):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_nft_fingerprint(self,mints)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_active_listings(self, first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        marketplaces: List[str]=None,
        limit: int=None,
        pagination_token: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_active_listings(self,first_verified_creators,verified_collection_addresses,marketplaces,limit,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_nft_metadata(self, mint_accounts: List[str]):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_nft_metadata(self,mint_accounts)
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
            return HeliusManager.get_raw_transactions(self,accounts,start_slot,end_slot,start_time,end_time,limit,sort_order,pagination_token)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_parsed_transactions(self, transactions: List[str], commitment: str=None):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_parsed_transactions(self,transactions,commitment)
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
            return HeliusManager.get_parsed_transaction_history(self,address,before,until,commitment,source,type)
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
            return HeliusManager.create_webhook(self,webhook_url,transaction_types,account_addresses,webhook_type,txn_status,auth_header)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_all_webhooks(self):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_all_webhooks(self)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_webhook(self, webhook_id: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.get_webhook(self,webhook_id)
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
            return HeliusManager.edit_webhook(self,webhook_id,webhook_url,transaction_types,account_addresses,webhook_type,txn_status,auth_header)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def delete_webhook(self, webhook_id: str):
        from agentipy.tools.use_helius import HeliusManager
        try:
            return HeliusManager.delete_webhook(self,webhook_id)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def fetch_token_report_summary(mint:str):
        from agentipy.tools.rugcheck import RugCheckManager
        try:
            return RugCheckManager.fetch_token_report_summary(mint)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def fetch_token_detailed_report(mint:str):
        from agentipy.tools.rugcheck import RugCheckManager
        try:
            return RugCheckManager.fetch_token_detailed_report(mint)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_pump_curve_state(conn: AsyncClient, curve_address: Pubkey,):
        from agentipy.tools.use_pumpfun import PumpfunManager
        try:
            return PumpfunManager.get_pump_curve_state(conn, curve_address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def calculate_pump_curve_price(curve_state:BondingCurveState):
        from agentipy.tools.use_pumpfun import PumpfunManager
        try:
            return PumpfunManager.calculate_pump_curve_price(curve_state)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def buy_token(self, mint:Pubkey, bonding_curve:Pubkey,associated_bonding_curve:Pubkey, amount:float, slippage:float,max_retries:int):
        from agentipy.tools.use_pumpfun import PumpfunManager
        try:
            return PumpfunManager.buy_token(self,mint,bonding_curve,associated_bonding_curve,amount,slippage,max_retries)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def sell_token(self, mint:Pubkey, bonding_curve:Pubkey,associated_bonding_curve:Pubkey, amount:float, slippage:float,max_retries:int):
        from agentipy.tools.use_pumpfun import PumpfunManager
        try:
            return PumpfunManager.sell_token(self, mint, bonding_curve, associated_bonding_curve, slippage, max_retries)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def resolve_name_to_address(self, domain: str):
        from agentipy.tools.use_sns import NameServiceManager
        try:
            return NameServiceManager.resolve_name_to_address(self, domain)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_favourite_domain(self, owner: str):
        from agentipy.tools.use_sns import NameServiceManager
        try:
            return NameServiceManager.get_favourite_domain(self, owner)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_all_domains_for_owner(self, owner: str):
        from agentipy.tools.use_sns import NameServiceManager
        try:
            return NameServiceManager.get_all_domains_for_owner(self, owner)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_registration_transaction(self, domain: str, buyer: str, buyer_token_account: str, space: int, 
                                     mint: Optional[str] = None, referrer_key: Optional[str] = None):
        from agentipy.tools.use_sns import NameServiceManager
        try:
            return NameServiceManager.get_registration_transaction(self, domain, buyer, buyer_token_account, space, mint, referrer_key)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")

    async def deploy_collection(self, name: str, uri: str, royalty_basis_points: int, creator_address: str):
        from agentipy.tools.use_metaplex import DeployCollectionManager
        try:
            return DeployCollectionManager.deploy_collection(self, name, uri, royalty_basis_points, creator_address)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_metaplex_asset(self, assetId:str):
        from agentipy.tools.use_metaplex import DeployCollectionManager
        try:
            return DeployCollectionManager.get_metaplex_asset(self, assetId)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_metaplex_assets_by_creator(self,creator: str, onlyVerified: bool = False, sortBy: str | None = None, sortDirection: str | None = None,
    limit: int | None = None, page: int | None = None, before: str | None = None, after: str | None = None):
        from agentipy.tools.use_metaplex import DeployCollectionManager
        try:
            return DeployCollectionManager.get_metaplex_assets_by_creator(self, creator, onlyVerified, sortBy, sortDirection, limit, page, before, after)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def get_metaplex_assets_by_authority(self,authority: str, sortBy: str | None = None, sortDirection: str | None = None,
    limit: int | None = None, page: int | None = None, before: str | None = None, after: str | None = None):
        from agentipy.tools.use_metaplex import DeployCollectionManager
        try:
            return DeployCollectionManager.get_metaplex_assets_by_authority(self, authority, sortBy, sortDirection, limit, page, before, after)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def mint_metaplex_core_nft(self,collectionMint: str, name: str, uri: str, sellerFeeBasisPoints: int | None = None, address: str | None = None,
    share: str | None = None, recipient: str | None = None):
        from agentipy.tools.use_metaplex import DeployCollectionManager
        try:
            return DeployCollectionManager.mint_metaplex_core_nft(self, collectionMint, name, uri, sellerFeeBasisPoints, address, share, recipient)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def create_debridge_transaction(
    self,
    src_chain_id: str,
    src_chain_token_in: str,
    src_chain_token_in_amount: str,
    dst_chain_id: str,
    dst_chain_token_out: str,
    dst_chain_token_out_recipient: str,
    src_chain_order_authority_address: str,
    dst_chain_order_authority_address: str,
    affiliate_fee_percent: str = "0",
    affiliate_fee_recipient: str = "",
    prepend_operating_expenses: bool = True,
    dst_chain_token_out_amount: str = "auto"):
        from agentipy.tools.use_debridge import DeBridgeManager   
        try:
            return DeBridgeManager.create_debridge_transaction(self, src_chain_id, src_chain_token_in, src_chain_token_in_amount, dst_chain_id, dst_chain_token_out, dst_chain_token_out_recipient, src_chain_order_authority_address, dst_chain_order_authority_address, affiliate_fee_percent, affiliate_fee_recipient, prepend_operating_expenses, dst_chain_token_out_amount)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def execute_debridge_transaction(self, transaction_data: dict):
        from agentipy.tools.use_debridge import DeBridgeManager   
        try:
            return DeBridgeManager.execute_debridge_transaction(self, transaction_data)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
    async def check_transaction_status(self, tx_hash: str):
        from agentipy.tools.use_debridge import DeBridgeManager   
        try:
            return DeBridgeManager.check_transaction_status(self, tx_hash)
        except Exception as e:
            raise SolanaAgentKitError(f"Failed to {e}")
        
        
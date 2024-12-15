from dataclasses import dataclass

from solders.pubkey import Pubkey as PublicKey  # type: ignore


@dataclass
class AccountMeta:
    public_key: PublicKey | str
    is_signer: bool
    is_writable: bool

@dataclass
class PoolKeys:
    amm_id: PublicKey
    base_mint: PublicKey
    quote_mint: PublicKey
    base_decimals: int
    quote_decimals: int
    open_orders: PublicKey
    target_orders: PublicKey
    base_vault: PublicKey
    quote_vault: PublicKey
    market_id: PublicKey
    market_authority: PublicKey
    market_base_vault: PublicKey
    market_quote_vault: PublicKey
    bids: PublicKey
    asks: PublicKey
    event_queue: PublicKey
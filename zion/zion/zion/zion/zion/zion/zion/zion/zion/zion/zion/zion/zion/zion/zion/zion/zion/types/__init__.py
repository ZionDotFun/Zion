from dataclasses import dataclass
from typing import Optional, List, Union
from pydantic import BaseModel
from solders.pubkey import Pubkey

@dataclass
class Creator(BaseModel):
    address: str
    percentage: int

@dataclass
class CollectionOptions(BaseModel):
    name:str
    uri:str
    royalty_basis_points: Optional[int] = None
    creators: Optional[List[Creator]] = None

@dataclass
class CollectionDeployment(BaseModel):
    collection_address: Pubkey
    signature: bytes

@dataclass
class MintCollectionNFTResponse(BaseModel):
    mint: Pubkey
    metadata: Pubkey

@dataclass
class PumpfunTokenOptions(BaseModel):
    twitter: Optional[str] = None
    telegram: Optional[str] = None
    website: Optional[str] = None
    initial_liquidity_sol: Optional[float] = None
    slippage_bps: Optional[int] = None
    priority_fee: Optional[int] = None

@dataclass
class PumpfunLaunchResponse(BaseModel):
    signature: str
    mint: str
    metadata_uri: Optional[str] = None
    error: Optional[str] = None

@dataclass
class LuloAccountSettings(BaseModel):
    owner: str
    allowed_protocols: Optional[str] = None
    homebase: Optional[str] = None
    minimum_rate: str

@dataclass
class LuloAccountDetailsResponse(BaseModel):
    total_value: float
    interest_earned: float
    realtime_apy: float
    settings: LuloAccountSettings

@dataclass
class NetworkPerformanceMetrics:
    """Data structure for Solana network performance metrics."""
    transactions_per_second: float
    total_transactions: int
    sampling_period_seconds: int
    current_slot: int

@dataclass
class TokenDeploymentResult:
    """Result of a token deployment operation."""
    mint: Pubkey
    transaction_signature: str

@dataclass
class TokenLaunchResult:
    """Result of a token launch operation."""
    signature: str
    mint: str
    metadata_uri: str

@dataclass
class TransferResult:
    """Result of a transfer operation."""
    signature: str
    from_address: str
    to_address: str
    amount: float
    token: Optional[str] = None

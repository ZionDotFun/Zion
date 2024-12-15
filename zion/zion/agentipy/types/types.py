from typing import Optional, List, Union
from pydantic import BaseModel
from solders.pubkey import Pubkey

class Creator(BaseModel):
    address: str
    percentage: int

class CollectionOptions(BaseModel):
    name:str
    uri:str
    royalty_basis_points: Optional[int] = None
    creators: Optional[List[Creator]] = None

class CollectionDeployment(BaseModel):
    collection_address: Pubkey
    signature: bytes

class MintCollectionNFTResponse(BaseModel):
    mint: Pubkey
    metadata: Pubkey

class PumpfunTokenOptions(BaseModel):
    twitter: Optional[str] = None
    telegram: Optional[str] = None
    website: Optional[str] = None
    initial_liquidity_sol: Optional[float] = None
    slippage_bps: Optional[int] = None
    priority_fee: Optional[int] = None

class PumpfunLaunchResponse(BaseModel):
    signature: str
    mint: str
    metadata_uri: Optional[str] = None
    error: Optional[str] = None

class LuloAccountSettings(BaseModel):
    owner: str
    allowed_protocols: Optional[str] = None
    homebase: Optional[str] = None
    minimum_rate: str

class LuloAccountDetailsResponse(BaseModel):
    total_value: float
    interest_earned: float
    realtime_apy: float
    settings: LuloAccountSettings
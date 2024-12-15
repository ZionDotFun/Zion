import logging
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation, getcontext

from construct import Bytes, Enum, Int8ul, Int32ul, Int64ul, Padding, Struct
from solana.rpc.api import Client
from solders.pubkey import Pubkey  # type: ignore
from spl.token.instructions import get_associated_token_address

from agentipy.agent import SolanaAgentKit

from .constants import LAMPORTS_PER_SOL

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_EVEN

logger = logging.getLogger(__name__)

class TradeDirection:
    BUY = 'BUY'
    SELL = 'SELL'

curve_account_struct = Struct(
    Padding(8),
    "totalSupply" / Int64ul,
    "curveAmount" / Int64ul,
    "mint" / Bytes(32),
    "decimals" / Int8ul,
    "collateralCurrency" / Enum(Int8ul, Sol=0),
    "curveType" / Enum(Int8ul, LinearV1=0),
    "marketcapThreshold" / Int64ul,
    "marketcapCurrency" / Enum(Int8ul, Sol=0),
    "migrationFee" / Int64ul,
    "coefB" / Int32ul,
    "bump" / Int8ul
)

@dataclass
class CurveState:
    totalSupply: int
    curveAmount: int
    mint: str
    decimals: int
    collateralCurrency: str
    curveType: str
    marketcapThreshold: int
    marketcapCurrency: str
    migrationFee: int
    coefB: int
    bump: int

def get_curve_state(agent: SolanaAgentKit, mint_str: str):
    try:
        client = Client(agent.rpc_url)
        mint = Pubkey.from_string(mint_str)
        MOONSHOT_PROGRAM = Pubkey.from_string("MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG")
        SEED = "token".encode()

        curve_account, _ = Pubkey.find_program_address(
            [SEED, bytes(mint)],
            MOONSHOT_PROGRAM
        )

        account_info = client.get_account_info(curve_account)
        data = account_info.value.data
        parsed_data = curve_account_struct.parse(data)
        
        curve_state = CurveState(
            totalSupply=parsed_data.totalSupply,
            curveAmount=parsed_data.curveAmount,
            mint=str(Pubkey.from_bytes(parsed_data.mint)),
            decimals=parsed_data.decimals,
            collateralCurrency="Sol",
            curveType="LinearV1",
            marketcapThreshold=parsed_data.marketcapThreshold,
            marketcapCurrency="Sol",
            migrationFee=parsed_data.migrationFee,
            coefB=parsed_data.coefB,
            bump=parsed_data.bump
        )
        return curve_state
    
    except Exception as e:
        logger.error(f"Error occured while fetching curve data: {e}", exc_info=True)
        return None

def get_collateral_amount_by_tokens(mint_str: str, token_amount: float, direction: TradeDirection):
    
    token_amount = int(token_amount * LAMPORTS_PER_SOL)
    
    curve_state = get_curve_state(mint_str)
    if not curve_state:
        return None
    
    curve_position = curve_state.totalSupply - curve_state.curveAmount
    
    if direction == TradeDirection.SELL:
        curve_position -= token_amount
    
    collateral_amount = get_collateral_price(token_amount, curve_position)
    collateral_amount = round(collateral_amount / LAMPORTS_PER_SOL, 5)
    collateral_amount = int(collateral_amount * LAMPORTS_PER_SOL)
    return collateral_amount

def get_collateral_price(tokens_amount, curve_position):
    
    COEF_B = Decimal('10')
    COEF_A = Decimal('1.63471e-15')
    COLLATERAL_DECIMALS = Decimal('1e9')
    TOKEN_DECIMALS = Decimal('1e9')

    coef_b = (COEF_B / COLLATERAL_DECIMALS)

    n = (Decimal(tokens_amount) / TOKEN_DECIMALS).quantize(Decimal('1.00000000000000000000'))
    m = (Decimal(curve_position) / TOKEN_DECIMALS).quantize(Decimal('1.00000000000000000000'))

    result = ((Decimal('0.5') * COEF_A * n * (Decimal('2') * m + n) + coef_b * n) * COLLATERAL_DECIMALS).quantize(Decimal('1.00000000000000000000'))

    try:
        collateral_price = round(result)
    except InvalidOperation:
        raise ValueError('Expected collateral amount is 0 or undefined!')

    return collateral_price

def get_tokens_by_collateral_amount(mint_str: str, collateral_amount: float, direction: TradeDirection):
    try:
        collateral_amount = int(collateral_amount * LAMPORTS_PER_SOL)
        curve_state = get_curve_state(mint_str)
        
        if not curve_state:
            return None
        
        curve_position = curve_state.totalSupply - curve_state.curveAmount
        
        tokens = get_tokens_nr_from_collateral(
            collateral_amount,
            curve_position,
            direction
        )
        
        return int(tokens)
    except:
        return None

def get_tokens_nr_from_collateral(collateral_amount, curve_position, direction):
    # Constants
    COEF_B = Decimal('10')
    COEF_A = Decimal('1.63471e-15')
    TOKEN_DECIMALS = Decimal('1e9')
    COLLATERAL_DECIMALS = Decimal('1e9')
    
    y = (Decimal(collateral_amount) / COLLATERAL_DECIMALS).quantize(Decimal('1.00000000000000000000'))
    m = (Decimal(curve_position) / TOKEN_DECIMALS).quantize(Decimal('1.00000000000000000000'))

    coef_b = (COEF_B / COLLATERAL_DECIMALS)
    
    b = ((COEF_A * m + coef_b) * Decimal(2)).quantize(Decimal('1.00000000000000000000'))
    c = (y * Decimal(-2)).quantize(Decimal('1.00000000000000000000'))

    if direction == TradeDirection.SELL:
        b = -b
        c = -c

    discriminant = (b ** Decimal(2) - Decimal(4) * COEF_A * c).quantize(Decimal('1.00000000000000000000'))

    if discriminant < Decimal(0):
        raise ValueError('Negative discriminant, no real roots for tokensNr from collateral calculation')

    sqrt_discriminant = discriminant.sqrt().quantize(Decimal('1.00000000000000000000'))
    two_a = (Decimal(2) * COEF_A).quantize(Decimal('1.00000000000000000000'))

    x1 = ((-b + sqrt_discriminant) / two_a).quantize(Decimal('1.00000000000000000000'))
    x2 = ((-b - sqrt_discriminant) / two_a).quantize(Decimal('1.00000000000000000000'))
    x = x2 if direction == TradeDirection.SELL else x1

    result = int(round(x)) * int(TOKEN_DECIMALS)
    return result

def derive_curve_accounts(mint: Pubkey):
    try:
        MOONSHOT_PROGRAM = Pubkey.from_string("MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG")
        SEED = "token".encode()

        curve_account, _ = Pubkey.find_program_address(
            [SEED, bytes(mint)],
            MOONSHOT_PROGRAM
        )

        curve_token_account = get_associated_token_address(curve_account, mint)
        return curve_account, curve_token_account
    except Exception:
        return None, None
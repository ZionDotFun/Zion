import json
import os
from typing import Optional

from anchorpy import Program
from anchorpy import Provider as AnchorProvider
from anchorpy import provider as anchor_provider
from construct import Container
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey as PublicKey  # type: ignore
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address

from .constants import LBCLMM_PROGRAM_IDS
from .utils import (bin_id_to_bin_array_index,
                    compute_base_factor_from_fee_bps,
                    derive_bin_array_bitmap_extension,
                    derive_customizable_permissionless_lb_pair, derive_oracle,
                    derive_reserve, is_overflow_default_bin_array_bitmap)


async def create_customizable_permissionless_lb_pair(
    connection: AsyncClient,
    bin_step: int,
    token_x: PublicKey,
    token_y: PublicKey,
    active_id: int,
    fee_bps: int,
    activation_type: str,
    has_alpha_vault: bool,
    creator_key: PublicKey,
    activation_point: Optional[int] = None,
    opt: Optional[dict] = None,
):
    """
    Creates a customizable permissionless LB pair.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'idl.json')

    try:
        with open(json_path, 'r') as json_file:
            idl_data = json.load(json_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"IDL file not found at {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from {json_path}: {e}")

    provider = AnchorProvider(connection, {}, anchor_provider.DEFAULT_OPTIONS)
    program_id = opt.get("program_id") if opt else LBCLMM_PROGRAM_IDS[opt.get("cluster")]
    program = Program(idl_data, program_id, provider)

    lb_pair, _ = derive_customizable_permissionless_lb_pair(token_x, token_y, program.program_id)
    reserve_x, _ = derive_reserve(token_x, lb_pair, program.program_id)
    reserve_y, _ = derive_reserve(token_y, lb_pair, program.program_id)
    oracle, _ = derive_oracle(lb_pair, program.program_id)

    active_bin_array_index = bin_id_to_bin_array_index(active_id)
    bin_array_bitmap_extension = (
        derive_bin_array_bitmap_extension(lb_pair, program.program_id)[0]
        if is_overflow_default_bin_array_bitmap(active_bin_array_index)
        else None
    )
    ix_data = Container(
        activeId=active_id,
        binStep=bin_step,
        baseFactor=compute_base_factor_from_fee_bps(bin_step, fee_bps),
        activationType=activation_type,
        activationPoint=activation_point or None,
        hasAlphaVault=has_alpha_vault,
        padding=[0] * 64,
    )

    user_token_x = get_associated_token_address(token_x, creator_key)

    transaction = await program.methods.initialize_customizable_permissionless_lb_pair(ix_data).accounts(
        {
            "lbPair": lb_pair,
            "rent": SYSVAR_RENT_PUBKEY,
            "reserveX": reserve_x,
            "reserveY": reserve_y,
            "binArrayBitmapExtension": bin_array_bitmap_extension,
            "tokenMintX": token_x,
            "tokenMintY": token_y,
            "tokenProgram": TOKEN_PROGRAM_ID,
            "oracle": oracle,
            "systemProgram": SYSTEM_PROGRAM_ID,
            "userTokenX": user_token_x,
            "funder": creator_key,
        }
    ).transaction()

    return transaction

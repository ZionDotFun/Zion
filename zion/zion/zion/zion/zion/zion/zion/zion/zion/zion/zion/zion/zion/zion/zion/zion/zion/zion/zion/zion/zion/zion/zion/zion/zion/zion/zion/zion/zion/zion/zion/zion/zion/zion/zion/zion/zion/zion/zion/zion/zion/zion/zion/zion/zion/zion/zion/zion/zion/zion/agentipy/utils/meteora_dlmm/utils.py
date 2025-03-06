from typing import Tuple

from solders.pubkey import Pubkey as PublicKey  # type: ignore

from agentipy.utils.meteora_dlmm.helpers import BN  # type: ignore

from .constants import BIN_ARRAY_BITMAP_SIZE, ILM_BASE, MAX_BIN_ARRAY_SIZE


def sort_token_mints(token_x: PublicKey, token_y: PublicKey) -> Tuple[PublicKey, PublicKey]:
    """Sorts two public keys and returns the minimum and maximum."""
    min_key, max_key = (token_y, token_x) if bytes(token_x) > bytes(token_y) else (token_x, token_y)
    return min_key, max_key


def derive_customizable_permissionless_lb_pair(
    token_x: PublicKey, token_y: PublicKey, program_id: PublicKey
) -> Tuple[PublicKey, int]:
    """Derives the customizable permissionless LB pair address."""
    min_key, max_key = sort_token_mints(token_x, token_y)
    seeds = [bytes(ILM_BASE), bytes(min_key), bytes(max_key)]
    return PublicKey.find_program_address(seeds, program_id)


def derive_reserve(token: PublicKey, lb_pair: PublicKey, program_id: PublicKey) -> Tuple[PublicKey, int]:
    """Derives the reserve address."""
    seeds = [bytes(lb_pair), bytes(token)]
    return PublicKey.find_program_address(seeds, program_id)


def derive_oracle(lb_pair: PublicKey, program_id: PublicKey) -> Tuple[PublicKey, int]:
    """Derives the oracle address."""
    seeds = [b"oracle", bytes(lb_pair)]
    return PublicKey.find_program_address(seeds, program_id)


def derive_bin_array(lb_pair: PublicKey, index: int, program_id: PublicKey) -> Tuple[PublicKey, int]:
    """Derives the bin array address."""
    if index < 0:
        bin_array_bytes = index.to_bytes(8, "little", signed=True)
    else:
        bin_array_bytes = index.to_bytes(8, "little")
    seeds = [b"bin_array", bytes(lb_pair), bin_array_bytes]
    return PublicKey.find_program_address(seeds, program_id)


def bin_id_to_bin_array_index(bin_id: int) -> int:
    """Converts a bin ID to a bin array index."""
    div, mod = divmod(bin_id, MAX_BIN_ARRAY_SIZE)
    return div - 1 if bin_id < 0 and mod != 0 else div


def is_overflow_default_bin_array_bitmap(bin_array_index: int) -> bool:
    """Checks if a bin array index overflows the default bitmap."""
    min_bin_array_index, max_bin_array_index = internal_bitmap_range()
    return bin_array_index > max_bin_array_index or bin_array_index < min_bin_array_index


def derive_bin_array_bitmap_extension(lb_pair: PublicKey, program_id: PublicKey) -> Tuple[PublicKey, int]:
    """Derives the bin array bitmap extension."""
    seeds = [b"bitmap", bytes(lb_pair)]
    return PublicKey.find_program_address(seeds, program_id)


def internal_bitmap_range() -> Tuple[int, int]:
    """Returns the internal bitmap range."""
    lower_bin_array_index = -BIN_ARRAY_BITMAP_SIZE
    upper_bin_array_index = BIN_ARRAY_BITMAP_SIZE - 1
    return lower_bin_array_index, upper_bin_array_index

def compute_base_factor_from_fee_bps(bin_step: BN, fee_bps: BN) -> BN:
    U16_MAX = 65535
    BASIS_POINT_MAX = 10000  # Assuming this constant exists, as it's not defined in your original code

    # Calculate the computed base factor
    computed_base_factor = (fee_bps * BASIS_POINT_MAX) / bin_step

    # Sanity check
    computed_base_factor_floor = int(computed_base_factor)  # Floor of the base factor
    
    if computed_base_factor != computed_base_factor_floor:
        if computed_base_factor_floor >= U16_MAX:
            raise ValueError("Base factor for the given fee bps overflow u16")

        if computed_base_factor_floor == 0:
            raise ValueError("Base factor for the given fee bps underflow")

        if computed_base_factor % 1 != 0:
            raise ValueError("Couldn't compute base factor for the exact fee bps")

    return BN(computed_base_factor_floor)

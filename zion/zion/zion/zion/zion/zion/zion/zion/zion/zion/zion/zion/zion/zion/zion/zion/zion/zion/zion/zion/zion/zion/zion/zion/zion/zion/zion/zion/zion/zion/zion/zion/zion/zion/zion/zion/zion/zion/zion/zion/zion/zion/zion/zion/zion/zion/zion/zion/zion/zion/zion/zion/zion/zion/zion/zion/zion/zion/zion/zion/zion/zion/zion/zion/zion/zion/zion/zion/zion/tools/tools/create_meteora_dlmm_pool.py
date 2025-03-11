import logging
from math import ceil
from typing import Optional

from solders.pubkey import Pubkey as PublicKey  # type: ignore
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID

from agentipy.agent import SolanaAgentKit
from agentipy.utils import meteora_dlmm as DLMM
from agentipy.utils.meteora_dlmm.types import ActivationType

logger = logging.getLogger(__name__)

class MeteoraManager:
    @staticmethod
    async def create_meteora_dlmm_pool(
    agent: SolanaAgentKit,
    bin_step: int,
    token_a_mint: PublicKey,
    token_b_mint: PublicKey,
    initial_price: float,
    price_rounding_up: bool,
    fee_bps: int,
    activation_type: ActivationType,
    has_alpha_vault: bool,
    activation_point: Optional[int]
) -> str:
        """
        Create Meteora DLMM pool.
        
        Args:
            agent: Instance of SolanaAgentKit.
            bin_step: DLMM pool bin step.
            token_a_mint: Mint of Token A.
            token_b_mint: Mint of Token B.
            initial_price: Initial pool price as tokenA/tokenB ratio.
            price_rounding_up: Whether to round up the initial pool price.
            fee_bps: Pool trading fee in basis points.
            activation_type: Pool activation type (Timestamp or Slot).
            has_alpha_vault: Whether the pool has a Meteora alpha vault.
            activation_point: Activation point, depending on activation type, or None if not applicable.
        
        Returns:
            The transaction signature of the initialization.
        """
        connection = agent.connection

        token_a = Token(conn=connection,pubkey=token_a_mint,program_id=TOKEN_PROGRAM_ID,payer=agent.wallet)
        token_b = Token(conn=connection,pubkey=token_b_mint,program_id=TOKEN_PROGRAM_ID,payer=agent.wallet)

        token_a_mint_info = await token_a.get_mint_info()
        token_b_mint_info = await token_b.get_mint_info()

        init_price = DLMM.get_price_per_lamport(
            token_a_mint_info.decimals,
            token_b_mint_info.decimals,
            initial_price
        )

        activate_bin_id = DLMM.get_bin_id_from_price(
            initial_price,
            bin_step,
            not price_rounding_up
        )

        init_pool_tx = await DLMM.create_customizable_permissionless_lb_pair(
            connection=connection,
            bin_step=bin_step,
            token_x=token_a_mint,
            token_y=token_b_mint,
            active_id=int(activate_bin_id),
            fee_bps=fee_bps,
            activation_type=activation_type,
            has_alpha_vault=has_alpha_vault,
            creator_key=agent.wallet_address,
            activation_point=activation_point
        )

        try:
            tx_signature = await connection.send_and_confirm_transaction(
                init_pool_tx,
                [agent.wallet]
            )
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            raise e

        return tx_signature

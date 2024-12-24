from typing import Dict, Optional

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey  # type: ignore
from solders.rpc.responses import GetTokenAccountsByOwnerResp  # type: ignore

from agentipy.agent import SolanaAgentKit
from agentipy.constants import LAMPORTS_PER_SOL


async def get_balance(
    agent: SolanaAgentKit,
    token_address: Optional[Pubkey] = None
) -> Optional[float]:
    """
    Get the balance of SOL or an SPL token for the agent's wallet.

    Args:
        agent: SolanaAgentKit instance
        token_address: Optional SPL token mint address. If not provided, returns SOL balance.

    Returns:
        Balance as a float in UI units, or None if the account doesn't exist.

    Raises:
        Exception: If the balance check fails.
    """
    try:
        if not token_address:
            response = await agent.connection.get_balance(
                agent.wallet_address,
                commitment=Confirmed
            )
            return response.value / LAMPORTS_PER_SOL

        response = await agent.connection.get_token_account_balance(
            token_address,
            commitment=Confirmed
        )

        if response.value is None:
            return None

        return float(response.value.ui_amount)

    except Exception as error:
        raise Exception(f"Failed to get balance: {str(error)}") from error

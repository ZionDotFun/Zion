from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.transaction import Transaction
from solders.system_program import CreateAccountParams, create_account
from solana.keypair import Keypair
from spl.token.instructions import initialize_mint2, MINT_SIZE
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from typing import Dict, Any


from agentipy.agent import SolanaAgentKit


import asyncio
import logging

logger = logging.getLogger(__name__)


async def get_minimum_balance_for_rent_exemption(connection: AsyncClient) -> int:
    """
    Get the minimum balance for rent exemption for an account of MINT_SIZE.

    Args:
        connection: Async Solana RPC client.

    Returns:
        Minimum balance in lamports required for rent exemption.
    """
    lamports = await connection.get_minimum_balance_for_rent_exemption(MINT_SIZE)
    return lamports


async def deploy_token(agent:SolanaAgentKit, decimals: int = 9) -> Dict[str, Any]:
    """
    Deploy a new SPL token.

    Args:
        agent: SolanaAgentKit instance with wallet and connection.
        decimals: Number of decimals for the token (default: 9).

    Returns:
        A dictionary containing the token mint address.
    """
    try:
        
        mint = Keypair()
        logger.info(f"Generated mint address: {mint.public_key}")

        
        lamports = await get_minimum_balance_for_rent_exemption(agent.connection)

        
        create_account_ix = create_account(
            CreateAccountParams(
                from_pubkey=agent.wallet_address,
                to_pubkey=mint.public_key,
                lamports=lamports,
                space=MINT_SIZE,
                program_id=TOKEN_PROGRAM_ID,
            )
        )

        initialize_mint_ix = initialize_mint2(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.public_key,
            decimals=decimals,
            mint_authority=PublicKey(agent.wallet_address),
            freeze_authority=PublicKey(agent.wallet_address),
        )

        transaction = Transaction()
        transaction.add(create_account_ix, initialize_mint_ix)

        tx_signature = await agent.connection.send_transaction(
            transaction, agent.wallet, mint, opts={"preflight_commitment": Confirmed}
        )

        logger.info(f"Transaction Signature: {tx_signature}")

        return {
            "mint": str(mint.public_key),
            "signature": tx_signature,
        }

    except Exception as e:
        logger.error(f"Token deployment failed: {str(e)}")
        raise Exception(f"Token deployment failed: {str(e)}")
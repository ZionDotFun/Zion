from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solana.rpc.commitment import Confirmed
from solana.rpc.core import RPCException

from agentipy.constants import LAMPORTS_PER_SOL

async def request_faucet_funds(agent) -> str:
    """
    Request SOL from the Solana faucet (devnet/testnet only).

    Args:
        agent: An object with `connection` (AsyncClient) and `wallet_address` (str).

    Returns:
        str: The transaction signature.

    Raises:
        Exception: If the request fails or times out.
    """
    try:
        wallet_address = Pubkey.from_string(agent.wallet_address)
        tx_signature = await agent.connection.request_airdrop(wallet_address, 5 * LAMPORTS_PER_SOL)
        
        latest_blockhash = await agent.connection.get_latest_blockhash()
        await agent.connection.confirm_transaction(
            tx_signature, 
            commitment=Confirmed, 
            last_valid_block_height=latest_blockhash.value.last_valid_block_height
        )

        return tx_signature
    except RPCException as e:
        raise Exception(f"Faucet request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

import base64
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
import aiohttp

from agentipy.agent import SolanaAgentKit



async def stake_with_jup(agent: SolanaAgentKit, amount: float) -> str:
    """
    Stake SOL with Jup validator.

    Args:
        agent (SolanaAgentKit): The agent instance for Solana interaction.
        amount (float): The amount of SOL to stake.

    Returns:
        str: The transaction signature.

    Raises:
        Exception: If the staking process fails.
    """
    try:

        url = f"https://worker.jup.ag/blinks/swap/So11111111111111111111111111111111111111112/jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v/{amount}"
        payload = {"account": str(agent.wallet_address)}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as res:
                if res.status != 200:
                    raise Exception(f"Failed to fetch transaction: {res.status}")

                data = await res.json()

        
        txn = VersionedTransaction.deserialize(base64.b64decode(data["transaction"]))

        latest_blockhash = await agent.connection.get_latest_blockhash()
        txn.message.recent_blockhash = latest_blockhash.value.blockhash

        txn.sign([agent.wallet])

        signature = await agent.connection.send_raw_transaction(
            txn.serialize(),
            opts={"skip_preflight": False, "max_retries": 3},
        )

        await agent.connection.confirm_transaction(
            signature,
            commitment=Confirmed,
            last_valid_block_height=latest_blockhash.value.last_valid_block_height,
        )

        return str(signature)

    except Exception as e:
        raise Exception(f"jupSOL staking failed: {str(e)}")

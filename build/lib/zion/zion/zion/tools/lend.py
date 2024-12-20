import base64
import json

from solana.rpc.commitment import Confirmed
from solders.transaction import VersionedTransaction  # type: ignore

from agentipy.agent import SolanaAgentKit


async def lend_asset(agent: SolanaAgentKit, amount: float) -> str:
    """
    Lend tokens for yields using Lulo API.

    Args:
        agent (SolanaAgentKit): SolanaAgentKit instance with connection and wallet.
        amount (float): Amount of USDC to lend.

    Returns:
        str: Transaction signature.
    """
    try:
        url = f"https://blink.lulo.fi/actions?amount={amount}&symbol=USDC"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"account": str(agent.wallet.pubkey())})

        async with agent.session.post(url, headers=headers, data=payload) as response:
            if response.status != 200:
                raise Exception(f"Lulo API Error: {response.status}")
            data = await response.json()

        transaction_bytes = base64.b64decode(data["transaction"])
        lulo_txn = VersionedTransaction.deserialize(transaction_bytes)

        latest_blockhash = await agent.connection.get_latest_blockhash()
        lulo_txn.message.recent_blockhash = latest_blockhash.value.blockhash

        lulo_txn.sign([agent.wallet])

        signature = await agent.connection.send_transaction(lulo_txn, opts={"preflight_commitment": Confirmed})
        
        await agent.connection.confirm_transaction(
            tx_sig=signature,
            last_valid_block_height=latest_blockhash.value.last_valid_block_height,
            commitment=Confirmed,
        )

        return str(signature)

    except Exception as e:
        raise Exception(f"Lending failed: {str(e)}")

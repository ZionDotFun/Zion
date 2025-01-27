import base64
import json

import aiohttp
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solders.message import to_bytes_versioned  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore

from agentipy.agent import SolanaAgentKit
from agentipy.helpers import fix_asyncio_for_windows

fix_asyncio_for_windows()

class AssetLender:
    @staticmethod
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

            session = aiohttp.ClientSession()

            async with session.post(url, headers=headers, data=payload) as response:
                if response.status != 200:
                    raise Exception(f"Lulo API Error: {response.status}")
                data = await response.json()

            transaction_bytes = base64.b64decode(data["transaction"])
            lulo_txn = VersionedTransaction.from_bytes(transaction_bytes)

            latest_blockhash = await agent.connection.get_latest_blockhash()

            signature = agent.wallet.sign_message(to_bytes_versioned(lulo_txn.message))

            signed_tx = VersionedTransaction.populate(lulo_txn.message, [signature])

            tx_resp = await agent.connection.send_transaction(
                signed_tx,
                opts=TxOpts(preflight_commitment=Confirmed)
            )          
            tx_id = tx_resp.value 

            await agent.connection.confirm_transaction(
                tx_id,
                commitment=Confirmed,
                last_valid_block_height=latest_blockhash.value.last_valid_block_height,
            )

            return str(signature)

        except Exception as e:
            raise Exception(f"Lending failed: {str(e)}")

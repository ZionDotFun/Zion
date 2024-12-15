from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.core import RPCException
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey  # type: ignore

from agentipy.agent import SolanaAgentKit
from agentipy.constants import LAMPORTS_PER_SOL


class FaucetManager:
    @staticmethod
    async def request_faucet_funds(agent: SolanaAgentKit) -> str:
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
            print(f"Requesting faucet for wallet: {repr(agent.wallet_address)}")

            response = await agent.connection.request_airdrop(
                agent.wallet_address, 5 * LAMPORTS_PER_SOL
            )

            latest_blockhash = await agent.connection.get_latest_blockhash()
            await agent.connection.confirm_transaction(
                response.value,
                commitment=Confirmed,
                last_valid_block_height=latest_blockhash.value.last_valid_block_height
            )

            print(f"Airdrop successful, transaction signature: {response.value}")
            return response.value
        except KeyError:
            raise Exception("Airdrop response did not contain a transaction signature.")
        except RPCException as e:
            raise Exception(f"Faucet request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")
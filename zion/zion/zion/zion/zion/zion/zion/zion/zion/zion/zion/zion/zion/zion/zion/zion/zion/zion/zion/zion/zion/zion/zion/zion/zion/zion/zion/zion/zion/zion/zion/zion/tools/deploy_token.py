import logging
from typing import Any, Dict

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.system_program import CreateAccountParams, create_account
from solders.transaction import Transaction  # type: ignore
from spl.token.constants import MINT_LEN, TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_mint

from agentipy.agent import SolanaAgentKit

logger = logging.getLogger(__name__)

class TokenDeploymentManager:
    @staticmethod
    async def get_minimum_balance_for_rent_exemption(connection: AsyncClient) -> int:
        """
        Get the minimum balance for rent exemption for an account of MINT_SIZE.

        Args:
            connection: Async Solana RPC client.

        Returns:
            Minimum balance in lamports required for rent exemption.
        """
        lamports = await connection.get_minimum_balance_for_rent_exemption(MINT_LEN)
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
            logger.info(f"Generated mint address: {mint.pubkey()}")

            
            lamports = await TokenDeploymentManager.get_minimum_balance_for_rent_exemption(agent.connection)

            
            create_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=agent.wallet_address,
                    to_pubkey=mint.pubkey(),
                    lamports=lamports,
                    space=MINT_LEN,
                    program_id=TOKEN_PROGRAM_ID,
                )
            )

            initialize_mint_ix = initialize_mint(
                program_id=TOKEN_PROGRAM_ID,
                mint=mint.pubkey(),
                decimals=decimals,
                mint_authority=Pubkey.from_string(agent.wallet_address),
                freeze_authority=Pubkey.from_string(agent.wallet_address),
            )

            transaction = Transaction()
            transaction.add(create_account_ix, initialize_mint_ix)

            tx_signature = await agent.connection.send_transaction(
                transaction, agent.wallet, mint, opts={"preflight_commitment": Confirmed}
            )

            logger.info(f"Transaction Signature: {tx_signature}")

            return {
                "mint": str(mint.pubkey()),
                "signature": tx_signature,
            }

        except Exception as e:
            logger.error(f"Token deployment failed: {str(e)}")
            raise Exception(f"Token deployment failed: {str(e)}")
import math
import logging

from typing import Optional, Dict, Any
from dataclasses import dataclass

from solders.pubkey import Pubkey
from solders.transaction import Transaction

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID, LAMPORTS_PER_SOL
from spl.token.instructions import get_associated_token_address, transfer as spl_transfer, transfer_checked


from agentipy.agent import SolanaAgentKit
# from solana_agentkit.types.account import TransferParams, transfer

logger = logging.getLogger(__name__)

@dataclass
class TransferResult:
    """Result of a transfer operation."""
    signature: str
    from_address: str
    to_address: str
    amount: float
    token: Optional[str] = None

class SolanaTransferHelper:
    """Helper class for Solana token and SOL transfers."""

    @staticmethod
    async def transfer_native_sol(agent: SolanaAgentKit, to: Pubkey, amount: float) -> str:
        """
        Transfer native SOL.

        Args:
            agent: SolanaAgentKit instance
            to: Recipient's public key
            amount: Amount of SOL to transfer

        Returns:
            Transaction signature.
        """
        transaction = Transaction()
        transaction.add(
            Transaction(
                from_pubkey=agent.wallet_address,
                to_pubkey=to,
                lamports=int(amount * LAMPORTS_PER_SOL)
            )
        )

        result = await agent.connection.send_transaction(
            transaction,
            [agent.wallet],
            opts={
                "skip_preflight": False,
                "preflight_commitment": Confirmed,
                "max_retries": 3
            }
        )

        return result.value.signature

    @staticmethod
    async def transfer_spl_tokens(
        rpc_client: AsyncClient,
        agent:SolanaAgentKit,
        recipient: Pubkey,
        spl_token: Pubkey,
        amount: float,
    ) -> str:
        """
        Transfer SPL tokens from payer to recipient.

        Args:
            rpc_client: Async RPC client instance.
            payer: Payer's public key (wallet address).
            recipient: Recipient's public key.
            spl_token: SPL token mint address.
            amount: Amount of tokens to transfer.

        Returns:
            Transaction signature.
        """
        
        spl_client = AsyncToken(rpc_client, spl_token, TOKEN_PROGRAM_ID, agent.wallet_address)
        
        mint = await spl_client.get_mint_info()
        if not mint.is_initialized:
            raise ValueError("Token mint is not initialized.")

        token_decimals = mint.decimals
        if amount < 10 ** -token_decimals:
            raise ValueError("Invalid amount of decimals for the token.")

        tokens = math.floor(amount * (10 ** token_decimals))

        payer_ata = get_associated_token_address(agent.wallet_address, spl_token)
        recipient_ata = get_associated_token_address(recipient, spl_token)

        payer_account_info = await spl_client.get_account_info(payer_ata)
        if not payer_account_info.is_initialized:
            raise ValueError("Payer's associated token account is not initialized.")
        if tokens > payer_account_info.amount:
            raise ValueError("Insufficient funds in payer's token account.")

        recipient_account_info = await spl_client.get_account_info(recipient_ata)
        if not recipient_account_info.is_initialized:
            raise ValueError("Recipient's associated token account is not initialized.")

        transfer_instruction = transfer_checked(
            amount=tokens,
            decimals=token_decimals,
            program_id=TOKEN_PROGRAM_ID,
            owner=agent.wallet_address,
            source=payer_ata,
            dest=recipient_ata,
            mint=spl_token,
        )

        # Build and send the transaction
        transaction = Transaction().add(transfer_instruction)
        response = await rpc_client.send_transaction(transaction,
        [agent.wallet],
        opts={
            "skip_preflight": False,
            "preflight_commitment": Confirmed,
            "max_retries": 3
        })

        return response["result"]

    @staticmethod
    async def confirm_transaction(agent: SolanaAgentKit, signature: str) -> None:
        """Wait for transaction confirmation."""
        await agent.connection.confirm_transaction(signature, commitment=Confirmed)

class TokenTransferManager:
    """Manages token and SOL transfers."""

    def __init__(self, agent: SolanaAgentKit):
        self.agent = agent
        self.transfer_history: list[TransferResult] = []

    async def execute_transfer(self, to: Pubkey, amount: float, mint: Optional[Pubkey] = None) -> TransferResult:
        """
        Execute a token or SOL transfer.

        Args:
            to: Recipient's public key
            amount: Amount to transfer
            mint: Token mint address (None for SOL transfers)

        Returns:
            TransferResult containing transfer details.
        """
        try:
            if mint:
                signature = await SolanaTransferHelper.transfer_spl_tokens(self.agent, to, amount, mint)
                token_identifier = str(mint)
            else:
                signature = await SolanaTransferHelper.transfer_native_sol(self.agent, to, amount)
                token_identifier = "SOL"

            await SolanaTransferHelper.confirm_transaction(self.agent, signature)

            result = TransferResult(
                signature=signature,
                from_address=str(self.agent.wallet_address),
                to_address=str(to),
                amount=amount,
                token=token_identifier
            )

            self.transfer_history.append(result)
            return result

        except Exception as error:
            logger.error(f"Transfer failed: {error}")
            raise RuntimeError(f"Transfer operation failed: {error}") from error

    async def verify_transfer(self, transfer_result: TransferResult) -> bool:
        """
        Verify that a transfer was successful.

        Args:
            transfer_result: TransferResult to verify

        Returns:
            True if the transfer succeeded, False otherwise.
        """
        try:
            transaction_info = await self.agent.connection.get_transaction(
                transfer_result.signature,
                commitment=Confirmed
            )
            return transaction_info.value.meta.err is None
        except Exception as error:
            logger.warning(f"Failed to verify transfer: {error}")
            return False

    def get_transfer_history(self) -> list[TransferResult]:
        """Retrieve the history of all executed transfers."""
        return self.transfer_history.copy()

from typing import Optional, Dict
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solana.rpc.async_api import AsyncClient
from solders.rpc.responses import GetTokenAccountsByOwnerResp
from spl.token.constants import LAMPORTS_PER_SOL
from agentipy.agent import SolanaAgentKit

LAMPORTS_PER_SOL = 1000000000  # 1 SOL = 1 billion lamports

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

async def get_token_accounts(
    agent: 'SolanaAgentKit',
    token_address: Pubkey
) -> list:
    """
    Get all token accounts owned by the wallet for a specific token.
    
    Args:
        agent: SolanaAgentKit instance
        token_address: Token mint address
        
    Returns:
        List of token account addresses
    """
    try:
        response = await agent.connection.get_token_accounts_by_owner(
            agent.wallet_address,
            {'mint': token_address}
        )
        
        return [account.pubkey for account in response.value]
    except Exception as error:
        raise Exception(f"Failed to get token accounts: {str(error)}") from error


async def get_all_token_balances(
    agent: SolanaAgentKit
) -> Dict[str, float]:
    """
    Get balances for all tokens owned by the wallet.

    Args:
        agent: SolanaAgentKit instance.

    Returns:
        Dictionary mapping token addresses to their balances.

    Raises:
        Exception: If fetching balances fails.
    """
    try:
        response: GetTokenAccountsByOwnerResp = await agent.connection.get_token_accounts_by_owner(
            owner=agent.wallet_address,
            opts=TokenAccountOpts(program_id=Pubkey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
        )

        balances = {}
        for account in response.value:
            token_balance = await agent.connection.get_token_account_balance(
                account.pubkey
            )

            if token_balance.value.ui_amount > 0:
                balances[str(account.account.mint)] = token_balance.value.ui_amount

        return balances

    except Exception as error:
        raise Exception(f"Failed to fetch all token balances: {str(error)}") from error

class BalanceMonitor:
    """Helper class for monitoring balances over time."""

    def __init__(self, agent: SolanaAgentKit):
        self.agent = agent
        self.previous_balances: Dict[str, float] = {}

    async def update_and_get_changes(
        self,
        token_address: Optional[Pubkey] = None
    ) -> Dict[str, float]:
        """
        Update balances and get changes since the last check.

        Args:
            token_address: Optional specific token to monitor.

        Returns:
            Dictionary containing current balance and change.
        """
        current_balance = await get_balance(self.agent, token_address)
        token_key = str(token_address) if token_address else 'SOL'

        previous_balance = self.previous_balances.get(token_key, 0.0)
        change = (current_balance or 0.0) - previous_balance

        self.previous_balances[token_key] = current_balance or 0.0

        return {
            'current_balance': current_balance,
            'previous_balance': previous_balance,
            'change': change
        }

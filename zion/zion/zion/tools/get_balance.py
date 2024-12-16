from solders.pubkey import Pubkey
from agentipy.agent import SolanaAgentKit

LAMPORTS_PER_SOL = 1000000000  # 1 SOL = 1 billion lamports

def get_balance(agent: SolanaAgentKit, token_address: Pubkey = None):
    """
    Get the balance of SOL or an SPL token for the agent's wallet
    :param agent: SolanaAgentKit instance
    :param token_address: Optional SPL token mint address. If not provided, returns SOL balance
    :returns: Balance as a number (in UI units) or None if account doesn't exist
    """
    try:
        if not token_address:
            balance = agent.connection.get_balance(agent.wallet_address)
            return balance / LAMPORTS_PER_SOL
        
        token_account_balance = agent.connection.get_token_account_balance(token_address)
        return token_account_balance['result']['value']['uiAmount']
    except Exception as e:
        raise Exception(f"Failed to fetch balance: {str(e)}")

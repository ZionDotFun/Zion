import base64
import logging
import os

from solana.rpc.api import Client
from solana.rpc.commitment import Processed
from solana.rpc.types import TokenAccountOpts, TxOpts
from solders.compute_budget import set_compute_unit_limit  # type: ignore
from solders.compute_budget import set_compute_unit_price  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.system_program import (CreateAccountWithSeedParams,
                                    create_account_with_seed)
from solders.transaction import VersionedTransaction  # type: ignore
from spl.token.client import Token
from spl.token.instructions import (CloseAccountParams,
                                    InitializeAccountParams, close_account,
                                    create_associated_token_account,
                                    get_associated_token_address,
                                    initialize_account)

from agentipy.agent import SolanaAgentKit
from agentipy.utils.raydium.constants import (SOL_DECIMAL, TOKEN_PROGRAM_ID,
                                              UNIT_BUDGET, UNIT_PRICE, WSOL)
from agentipy.utils.raydium.layouts import ACCOUNT_LAYOUT
from agentipy.utils.raydium.utils import (confirm_txn, fetch_pool_keys,
                                          get_token_balance,
                                          get_token_reserves,
                                          make_swap_instruction,
                                          sol_for_tokens, tokens_for_sol)

logger = logging.getLogger(__name__)

class RaydiumManager:
    """
    Provides methods to perform buy and sell operations on Raydium liquidity pools.

    Static Methods:
        - buy_with_raydium: Executes a buy operation with specified SOL amount and slippage.
        - sell_with_raydium: Executes a sell operation with specified token percentage and slippage.
    """

    @staticmethod
    def buy_with_raydium(agent: SolanaAgentKit, pair_address: str, sol_in: float = 0.01, slippage: int = 5) -> bool:
        """
        Executes a buy operation on the specified Raydium pair.

        Args:
            agent (SolanaAgentKit): The agent containing wallet and RPC connection details.
            pair_address (str): The address of the Raydium pair to trade on.
            sol_in (float): Amount of SOL to use for the buy operation (default: 0.01 SOL).
            slippage (int): Allowed slippage percentage (default: 5%).

        Returns:
            bool: True if the transaction is confirmed, False otherwise.
        """
        try:
            client = Client(agent.rpc_url)
            payer_keypair = agent.wallet

            # Fetch pool keys and validate
            pool_keys = fetch_pool_keys(pair_address)
            if pool_keys is None:
                return False

            # Determine mint and calculate amounts
            mint = pool_keys.base_mint if pool_keys.base_mint != WSOL else pool_keys.quote_mint
            amount_in = int(sol_in * SOL_DECIMAL)
            base_reserve, quote_reserve, token_decimal = get_token_reserves(pool_keys)
            amount_out = sol_for_tokens(sol_in, base_reserve, quote_reserve)
            slippage_adjustment = 1 - (slippage / 100)
            minimum_amount_out = int(amount_out * slippage_adjustment * 10**token_decimal)

            # Check for or create token account
            token_account_check = client.get_token_accounts_by_owner(
                payer_keypair.pubkey(), TokenAccountOpts(mint), Processed
            )
            if token_account_check.value:
                token_account = token_account_check.value[0].pubkey
                token_account_instr = None
            else:
                token_account = get_associated_token_address(payer_keypair.pubkey(), mint)
                token_account_instr = create_associated_token_account(
                    payer_keypair.pubkey(), payer_keypair.pubkey(), mint
                )

            # Create WSOL account
            seed = base64.urlsafe_b64encode(os.urandom(24)).decode('utf-8')
            wsol_token_account = Pubkey.create_with_seed(payer_keypair.pubkey(), seed, TOKEN_PROGRAM_ID)
            balance_needed = Token.get_min_balance_rent_for_exempt_for_account(client)

            create_wsol_account_instr = create_account_with_seed(
                CreateAccountWithSeedParams(
                    from_pubkey=payer_keypair.pubkey(),
                    to_pubkey=wsol_token_account,
                    base=payer_keypair.pubkey(),
                    seed=seed,
                    lamports=int(balance_needed + amount_in),
                    space=ACCOUNT_LAYOUT.sizeof(),
                    owner=TOKEN_PROGRAM_ID
                )
            )

            init_wsol_account_instr = initialize_account(
                InitializeAccountParams(
                    program_id=TOKEN_PROGRAM_ID,
                    account=wsol_token_account,
                    mint=WSOL,
                    owner=payer_keypair.pubkey()
                )
            )

            # Create swap instructions
            swap_instructions = make_swap_instruction(
                amount_in=amount_in,
                minimum_amount_out=minimum_amount_out,
                token_account_in=wsol_token_account,
                token_account_out=token_account,
                accounts=pool_keys,
                owner=payer_keypair
            )

            # Close WSOL account after swap
            close_wsol_account_instr = close_account(
                CloseAccountParams(
                    program_id=TOKEN_PROGRAM_ID,
                    account=wsol_token_account,
                    dest=payer_keypair.pubkey(),
                    owner=payer_keypair.pubkey()
                )
            )

            # Compile instructions
            instructions = [
                set_compute_unit_limit(UNIT_BUDGET),
                set_compute_unit_price(UNIT_PRICE),
                create_wsol_account_instr,
                init_wsol_account_instr
            ]

            if token_account_instr:
                instructions.append(token_account_instr)

            instructions.extend([swap_instructions, close_wsol_account_instr])

            # Compile transaction
            compiled_message = MessageV0.try_compile(
                payer_keypair.pubkey(),
                instructions,
                [],
                client.get_latest_blockhash().value.blockhash,
            )

            # Send transaction
            txn_sig = client.send_transaction(
                txn=VersionedTransaction(compiled_message, [payer_keypair]),
                opts=TxOpts(skip_preflight=True)
            ).value

            # Confirm transaction
            return confirm_txn(txn_sig)

        except Exception as e:
            logger.error(f"Error during buy transaction {e}", exc_info=True)
            return False

    @staticmethod
    def sell_with_raydium(agent: SolanaAgentKit, pair_address: str, percentage: int = 100, slippage: int = 5) -> bool:
        """
        Executes a sell operation on the specified Raydium pair.

        Args:
            agent (SolanaAgentKit): The agent containing wallet and RPC connection details.
            pair_address (str): The address of the Raydium pair to trade on.
            percentage (int): Percentage of token balance to sell (default: 100%).
            slippage (int): Allowed slippage percentage (default: 5%).

        Returns:
            bool: True if the transaction is confirmed, False otherwise.
        """
        try:
            client = Client(agent.rpc_url)
            payer_keypair = agent.wallet
            logger.info(f"Starting sell transaction for pair address: {pair_address}")
            if not (1 <= percentage <= 100):
                logger.error("Percentage must be between 1 and 100.")
                return False

            logger.info("Fetching pool keys...")
            pool_keys = fetch_pool_keys(pair_address)
            if pool_keys is None:
                logger.error("No pool keys found...")
                return False
            logger.info("Pool keys fetched successfully.")

            mint = pool_keys.base_mint if pool_keys.base_mint != WSOL else pool_keys.quote_mint
            
            logger.info("Retrieving token balance...")
            token_balance = get_token_balance(str(mint))
            logger.info(f"Token Balance: {token_balance}")
            
            if token_balance == 0 or token_balance is None:
                logger.error("No token balance available to sell.")
                return False
            
            token_balance = token_balance * (percentage / 100)
            logger.info(f"Selling {percentage}% of the token balance, adjusted balance: {token_balance}")

            logger.info("Calculating transaction amounts...")
            base_reserve, quote_reserve, token_decimal = get_token_reserves(pool_keys)
            amount_out = tokens_for_sol(token_balance, base_reserve, quote_reserve)
            logger.info(f"Raw Amount Out: {amount_out}")
            
            slippage_adjustment = 1 - (slippage / 100)
            amount_out_with_slippage = amount_out * slippage_adjustment
            minimum_amount_out = int(amount_out_with_slippage * SOL_DECIMAL)
        
            amount_in = int(token_balance * 10**token_decimal)
            logger.info(f"Amount In: {amount_in} | Minimum Amount Out: {minimum_amount_out}")
            token_account = get_associated_token_address(payer_keypair.pubkey(), mint)
            
            logger.info("Generating seed and creating WSOL account...")
            seed = base64.urlsafe_b64encode(os.urandom(24)).decode('utf-8')
            wsol_token_account = Pubkey.create_with_seed(payer_keypair.pubkey(), seed, TOKEN_PROGRAM_ID)
            balance_needed = Token.get_min_balance_rent_for_exempt_for_account(client)
            
            create_wsol_account_instr = create_account_with_seed(
                CreateAccountWithSeedParams(
                    from_pubkey=payer_keypair.pubkey(),
                    to_pubkey=wsol_token_account,
                    base=payer_keypair.pubkey(),
                    seed=seed,
                    lamports=int(balance_needed),
                    space=ACCOUNT_LAYOUT.sizeof(),
                    owner=TOKEN_PROGRAM_ID
                )
            )
            
            init_wsol_account_instr = initialize_account(
                InitializeAccountParams(
                    program_id=TOKEN_PROGRAM_ID,
                    account=wsol_token_account,
                    mint=WSOL,
                    owner=payer_keypair.pubkey()
                )
            )

            logger.info("Creating swap instructions...")
            swap_instructions = make_swap_instruction(amount_in, minimum_amount_out, token_account, wsol_token_account, pool_keys, payer_keypair)
            
            logger.info("Preparing to close WSOL account after swap...")
            close_wsol_account_instr = close_account(CloseAccountParams(TOKEN_PROGRAM_ID, wsol_token_account, payer_keypair.pubkey(), payer_keypair.pubkey()))
            
            instructions = [
                set_compute_unit_limit(UNIT_BUDGET),
                set_compute_unit_price(UNIT_PRICE),
                create_wsol_account_instr,
                init_wsol_account_instr,
                swap_instructions,
                close_wsol_account_instr
            ]
            
            if percentage == 100:
                logger.info("Preparing to close token account after swap...")
                close_token_account_instr = close_account(
                    CloseAccountParams(TOKEN_PROGRAM_ID, token_account, payer_keypair.pubkey(), payer_keypair.pubkey())
                )
                instructions.append(close_token_account_instr)

            logger.info("Compiling transaction message...")
            compiled_message = MessageV0.try_compile(
                payer_keypair.pubkey(),
                instructions,
                [],  
                client.get_latest_blockhash().value.blockhash,
            )
            
            logger.info("Sending transaction...")
            txn_sig = client.send_transaction(
                txn = VersionedTransaction(compiled_message, [payer_keypair]), 
                opts = TxOpts(skip_preflight=True)
                ).value
            logger.info(f"Transaction Signature: {txn_sig}")

            logger.info("Confirming transaction...")
            confirmed = confirm_txn(txn_sig)
            
            logger.info(f"Transaction confirmed: {confirmed}")
            return confirmed
            
        except Exception as e:
            logger.error(f"Error occurred during transaction {e}", exc_info=True)
            return False
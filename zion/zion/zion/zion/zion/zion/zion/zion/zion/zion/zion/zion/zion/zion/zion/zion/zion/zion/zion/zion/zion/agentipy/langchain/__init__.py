import json

from langchain.tools import BaseTool
from solders.pubkey import Pubkey  # type: ignore

from agentipy.agent import SolanaAgentKit
from agentipy.tools import create_image
from agentipy.utils import toJSON
from agentipy.utils.meteora_dlmm.types import ActivationType


class SolanaBalanceTool(BaseTool):
    name:str = "solana_balance"
    description:str = """
    Get the balance of a Solana wallet or token account.

    If you want to get the balance of your wallet, you don't need to provide the tokenAddress.
    If no tokenAddress is provided, the balance will be in SOL.
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            token_address = Pubkey.from_string(input) if input else None
            balance = await self.solana_kit.get_balance(token_address)
            return {
                "status": "success",
                "balance": balance,
                "token": input or "SOL",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaTransferTool(BaseTool):
    name:str = "solana_transfer"
    description:str = """
    Transfer tokens or SOL to another address.

    Input (JSON string):
    {
        "to": "wallet_address",
        "amount": 1,
        "mint": "mint_address" (optional)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            recipient = Pubkey.from_string(data["to"])
            mint_address = Pubkey.from_string(data["mint"]) if "mint" in data else None

            transaction = await self.solana_kit.transfer(recipient, data["amount"], mint_address)

            return {
                "status": "success",
                "message": "Transfer completed successfully",
                "amount": data["amount"],
                "recipient": data["to"],
                "token": data.get("mint", "SOL"),
                "transaction": transaction,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaDeployTokenTool(BaseTool):
    name:str = "solana_deploy_token"
    description:str = """
    Deploy a new SPL token. Input should be JSON string with:
    {
        "decimals": 9,
        "initialSupply": 1000
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            decimals = data.get("decimals", 9)

            if decimals < 0 or decimals > 9:
                raise ValueError("Decimals must be between 0 and 9")

            token_details = await self.solana_kit.deploy_token(decimals)
            return {
                "status": "success",
                "message": "Token deployed successfully",
                "mintAddress": token_details["mint"],
                "decimals": decimals,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaTradeTool(BaseTool):
    name:str = "solana_trade"
    description:str = """
    Execute a trade on Solana.

    Input (JSON string):
    {
        "output_mint": "output_mint_address",
        "input_amount": 100,
        "input_mint": "input_mint_address" (optional),
        "slippage_bps": 100 (optional)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            output_mint = Pubkey.from_string(data["output_mint"])
            input_mint = Pubkey.from_string(data["input_mint"]) if "input_mint" in data else None
            slippage_bps = data.get("slippage_bps", 100)

            transaction = await self.solana_kit.trade(
                output_mint, data["input_amount"], input_mint, slippage_bps
            )

            return {
                "status": "success",
                "message": "Trade executed successfully",
                "transaction": transaction,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaFaucetTool(BaseTool):
    name:str = "solana_request_funds"
    description:str = "Request test funds from a Solana faucet."
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            result = await self.solana_kit.request_faucet_funds()
            return {
                "status": "success",
                "message": "Faucet funds requested successfully",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaStakeTool(BaseTool):
    name:str = "solana_stake"
    description:str = "Stake assets on Solana. Input is the amount to stake."
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            amount = int(input)
            result = await self.solana_kit.stake(amount)
            return {
                "status": "success",
                "message": "Assets staked successfully",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaGetWalletAddressTool(BaseTool):
    name:str = "solana_get_wallet_address"
    description:str = "Get the wallet address of the agent"
    solana_kit: SolanaAgentKit
    
    async def _arun(self):
        try:
            result = await self.solana_kit.wallet_address
            return {
                "status": "success",
                "message": "Wallet address fetched successfully",
                "result": str(result),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaCreateImageTool(BaseTool):
    name: str = "solana_create_image"
    description: str = """
    Create an image using OpenAI's DALL-E.

    Input (JSON string):
    {
        "prompt": "description of the image",
        "size": "image_size" (optional, default: "1024x1024"),
        "n": "number_of_images" (optional, default: 1)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            prompt = data["prompt"]
            size = data.get("size", "1024x1024")
            n = data.get("n", 1)

            if not prompt.strip():
                raise ValueError("Prompt must be a non-empty string.")

            result = await create_image(self.solana_kit, prompt, size, n)

            return {
                "status": "success",
                "message": "Image created successfully",
                "images": result["images"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR")
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaTPSCalculatorTool(BaseTool):
    name: str = "solana_get_tps"
    description: str = "Get the current TPS of the Solana network."
    solana_kit: SolanaAgentKit

    async def _arun(self):
        try:
            tps = await self.solana_kit.get_tps()

            return {
                "status": "success",
                "message": f"Solana (mainnet-beta) current transactions per second: {tps}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error fetching TPS: {str(e)}",
                "code": getattr(e, "code", "UNKNOWN_ERROR")
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaPumpFunTokenTool(BaseTool):
    name:str = "solana_launch_pump_fun_token"
    description:str = """
    Launch a Pump Fun token on Solana.

    Input (JSON string):
    {
        "token_name": "MyToken",
        "token_ticker": "MTK",
        "description": "A test token",
        "image_url": "http://example.com/image.png"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            result = await self.solana_kit.launch_pump_fun_token(
                data["token_name"],
                data["token_ticker"],
                data["description"],
                data["image_url"],
                options=data.get("options")
            )
            return {
                "status": "success",
                "message": "Pump Fun token launched successfully",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaFetchPriceTool(BaseTool):
    """
    Tool to fetch the price of a token in USDC.
    """
    name:str = "solana_fetch_price"
    description:str = """Fetch the price of a given token in USDC.

    Inputs:
    - tokenId: string, the mint address of the token, e.g., "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
    """
    solana_kit: SolanaAgentKit

    async def call(self, input: str) -> str:
        try:
            token_id = input.strip()
            price = await self.solana_kit.fetch_price(token_id)
            return json.dumps({
                "status": "success",
                "tokenId": token_id,
                "priceInUSDC": price,
            })
        except Exception as error:
            return json.dumps({
                "status": "error",
                "message": str(error),
                "code": getattr(error, "code", "UNKNOWN_ERROR"),
            })
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaTokenDataTool(BaseTool):
    """
    Tool to fetch token data for a given token mint address.
    """
    name:str = "solana_token_data"
    description:str = """Get the token data for a given token mint address.

    Inputs:
    - mintAddress: string, e.g., "So11111111111111111111111111111111111111112" (required)
    """
    solana_kit: SolanaAgentKit

    async def call(self, input: str) -> str:
        try:
            mint_address = input.strip()
            token_data = await self.solana_kit.get_token_data_by_address(mint_address)
            return json.dumps({
                "status": "success",
                "tokenData": token_data,
            })
        except Exception as error:
            return json.dumps({
                "status": "error",
                "message": str(error),
                "code": getattr(error, "code", "UNKNOWN_ERROR"),
            })
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaTokenDataByTickerTool(BaseTool):
    """
    Tool to fetch token data for a given token ticker.
    """
    name:str = "solana_token_data_by_ticker"
    description:str = """Get the token data for a given token ticker.

    Inputs:
    - ticker: string, e.g., "USDC" (required)
    """
    solana_kit: SolanaAgentKit

    async def call(self, input: str) -> str:
        try:
            ticker = input.strip()
            token_data = await self.solana_kit.get_token_data_by_ticker(ticker)
            return json.dumps({
                "status": "success",
                "tokenData": token_data,
            })
        except Exception as error:
            return json.dumps({
                "status": "error",
                "message": str(error),
                "code": getattr(error, "code", "UNKNOWN_ERROR"),
            })
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaMeteoraDLMMTool(BaseTool):
    """
    Tool to create dlmm pool on meteora.
    """
    name: str = "solana_create_meteora_dlmm_pool"
    description: str = """
    Create a Meteora DLMM Pool on Solana.

    Input (JSON string):
    {
        "bin_step": 5,
        "token_a_mint": "7S3d7xxFPgFhVde8XwDoQG9N7kF8Vo48ghAhoNxd34Zp",
        "token_b_mint": "A1b1xxFPgFhVde8XwDoQG9N7kF8Vo48ghAhoNxd34Zp",
        "initial_price": 1.23,
        "price_rounding_up": true,
        "fee_bps": 300,
        "activation_type": "Instant",  // Options: "Instant", "Delayed", "Manual"
        "has_alpha_vault": false,
        "activation_point": null      // Optional, only for Delayed type
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str) -> dict:
        try:
            # Parse input
            data = toJSON(input)

            # Ensure required keys exist
            required_keys = [
                "bin_step",
                "token_a_mint",
                "token_b_mint",
                "initial_price",
                "price_rounding_up",
                "fee_bps",
                "activation_type",
                "has_alpha_vault"
            ]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key: {key}")

            activation_type_mapping = {
                "Slot": ActivationType.Slot,
                "Timestamp": ActivationType.Timestamp,
            }
            activation_type = activation_type_mapping.get(data["activation_type"])
            if activation_type is None:
                raise ValueError("Invalid activation_type. Valid options are: Slot, Timestamp.")

            activation_point = data.get("activation_point", None)

            result = await self.solana_kit.create_meteora_dlmm_pool(
                bin_step=data["bin_step"],
                token_a_mint=data["token_a_mint"],
                token_b_mint=data["token_b_mint"],
                initial_price=data["initial_price"],
                price_rounding_up=data["price_rounding_up"],
                fee_bps=data["fee_bps"],
                activation_type=activation_type,
                has_alpha_vault=data["has_alpha_vault"],
                activation_point=activation_point
            )

            return {
                "status": "success",
                "message": "Meteora DLMM pool created successfully",
                "result": result,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to process input: {input}. Error: {str(e)}",
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaRaydiumBuyTool(BaseTool):
    name: str = "raydium_buy"
    description: str = """
    Buy tokens using Raydium's swap functionality.

    Input (JSON string):
    {
        "pair_address": "address_of_the_trading_pair",
        "sol_in": 0.01,  # Amount of SOL to spend (optional, defaults to 0.01)
        "slippage": 5  # Slippage tolerance in percentage (optional, defaults to 5)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            pair_address = data["pair_address"]
            sol_in = data.get("sol_in", 0.01)  # Default to 0.01 SOL if not provided
            slippage = data.get("slippage", 5)  # Default to 5% slippage if not provided

            result = await self.solana_kit.buy_with_raydium(pair_address, sol_in, slippage)

            return {
                "status": "success",
                "message": "Buy transaction completed successfully",
                "pair_address": pair_address,
                "sol_in": sol_in,
                "slippage": slippage,
                "transaction": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaRaydiumSellTool(BaseTool):
    name: str = "raydium_sell"
    description: str = """
    Sell tokens using Raydium's swap functionality.

    Input (JSON string):
    {
        "pair_address": "address_of_the_trading_pair",
        "percentage": 100,  # Percentage of tokens to sell (optional, defaults to 100)
        "slippage": 5  # Slippage tolerance in percentage (optional, defaults to 5)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            pair_address = data["pair_address"]
            percentage = data.get("percentage", 100)  # Default to 100% if not provided
            slippage = data.get("slippage", 5)  # Default to 5% slippage if not provided

            result = await self.solana_kit.sell_with_raydium(pair_address, percentage, slippage)

            return {
                "status": "success",
                "message": "Sell transaction completed successfully",
                "pair_address": pair_address,
                "percentage": percentage,
                "slippage": slippage,
                "transaction": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaBurnAndCloseTool(BaseTool):
    name: str = "solana_burn_and_close_account"
    description: str = """
    Burn and close a single Solana token account.

    Input: A JSON string with:
    {
        "token_account": "public_key_of_the_token_account"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            token_account = data["token_account"]

            if not token_account:
                raise ValueError("Token account is required.")

            result = await self.solana_kit.burn_and_close_accounts(token_account)

            return {
                "status": "success",
                "message": "Token account burned and closed successfully.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }
        
    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaBurnAndCloseMultipleTool(BaseTool):
    name: str = "solana_burn_and_close_multiple_accounts"
    description: str = """
    Burn and close multiple Solana token accounts.

    Input: A JSON string with:
    {
        "token_accounts": ["public_key_1", "public_key_2", ...]
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            token_accounts = data.get("token_accounts", [])

            if not isinstance(token_accounts, list) or not token_accounts:
                raise ValueError("A list of token accounts is required.")

            result = await self.solana_kit.multiple_burn_and_close_accounts(token_accounts)

            return {
                "status": "success",
                "message": "Token accounts burned and closed successfully.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaCreateGibworkTaskTool(BaseTool):
    name: str = "solana_create_gibwork_task"
    description: str = """
    Create an new task on Gibwork

    Input: A JSON string with:
    {
        "title": "title of the task",
        "content: "description of the task",
        "requirements": "requirements to complete the task",
        "tags": ["tag1", "tag2", ...] # list of tags associated with the task,
        "token_mint_address": "token mint address for payment",
        "token_amount": 1000 # amount of token to pay for the task
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            title = data["title"]
            content = data["content"]
            requirements = data["requirements"]
            tags = data.get("tags", [])
            token_mint_address = Pubkey.from_string(data["token_mint_address"])
            token_amount = data["token_amount"]
            
            result = await self.solana_kit.create_gibwork_task(title, content, requirements, tags, token_mint_address, token_amount)

            return {
                "status": "success",
                "message": "Token accounts burned and closed successfully.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }


    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaCreateGibworkTaskTool(BaseTool):
    name: str = "solana_create_gibwork_task"
    description: str = """
    Create an new task on Gibwork

    Input: A JSON string with:
    {
        "title": "title of the task",
        "content: "description of the task",
        "requirements": "requirements to complete the task",
        "tags": ["tag1", "tag2", ...] # list of tags associated with the task,
        "token_mint_address": "token mint address for payment",
        "token_amount": 1000 # amount of token to pay for the task
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            title = data["title"]
            content = data["content"]
            requirements = data["requirements"]
            tags = data.get("tags", [])
            token_mint_address = Pubkey.from_string(data["token_mint_address"])
            token_amount = data["token_amount"]
            
            result = await self.solana_kit.create_gibwork_task(title, content, requirements, tags, token_mint_address, token_amount)

            return {
                "status": "success",
                "message": "Token accounts burned and closed successfully.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaBuyUsingMoonshotTool(BaseTool):
    name: str = "solana_buy_using_moonshot"
    description:str = """
    Buy a token using Moonshot.

    Input: A JSON string with:
    {
        "mint_str": "string, the mint address of the token to buy",
        "collateral_amount": 0.01, # optional, collateral amount in SOL to use for the purchase (default: 0.01)
        "slippage_bps": 500 # optional, slippage in basis points (default: 500)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            mint_str = data["mint_str"]
            collateral_amount = data.get("collateral_amount", 0.01)
            slippage_bps = data.get("slippage_bps", 500)
            
            result = await self.solana_kit.buy_using_moonshot(mint_str, collateral_amount, slippage_bps)

            return {
                "status": "success",
                "message": "Token purchased successfully using Moonshot.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaSellUsingMoonshotTool(BaseTool):
    name: str = "solana_sell_using_moonshot"
    description:str = """
    Sell a token using Moonshot.

    Input: A JSON string with:
    {
        "mint_str": "string, the mint address of the token to sell",
        "token_balance": 0.01, # optional, token balance to sell (default: 0.01)
        "slippage_bps": 500 # optional, slippage in basis points (default: 500)
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            mint_str = data["mint_str"]
            token_balance = data.get("token_balance", 0.01)
            slippage_bps = data.get("slippage_bps", 500)
            
            result = await self.solana_kit.sell_using_moonshot(mint_str, token_balance, slippage_bps)

            return {
                "status": "success",
                "message": "Token sold successfully using Moonshot.",
                "result": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": getattr(e, "code", "UNKNOWN_ERROR"),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
            
class SolanaPythGetPriceTool(BaseTool):
    name: str = "solana_pyth_get_price"
    description: str = """
    Fetch the price of a token using the Pyth Oracle.

    Input: A JSON string with:
    {
        "mint_address": "string, the mint address of the token"
    }

    Output:
    {
        "price": float, # the token price (if trading),
        "confidence_interval": float, # the confidence interval (if trading),
        "status": "UNKNOWN", "TRADING", "HALTED", "AUCTION", "IGNORED",
        "message": "string, if not trading"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            mint_address = data["mint_address"]

            result = await self.solana_kit.pythFetchPrice(mint_address)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaHeliusGetBalancesTool(BaseTool):
    name: str = "solana_helius_get_balances"
    description: str = """
    Fetch the balances for a given Solana address.

    Input: A JSON string with:
    {
        "address": "string, the Solana address"
    }

    Output: {
        "balances": List[dict], # the list of token balances for the address
        "status": "success" or "error",
        "message": "Error message if any"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            address = data["address"]

            result = await self.solana_kit.get_balances(address)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")


class SolanaHeliusGetAddressNameTool(BaseTool):
    name: str = "solana_helius_get_address_name"
    description: str = """
    Fetch the name of a given Solana address.

    Input: A JSON string with:
    {
        "address": "string, the Solana address"
    }

    Output: {
        "name": "string, the name of the address",
        "status": "success" or "error",
        "message": "Error message if any"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            address = data["address"]

            result = await self.solana_kit.get_address_name(address)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")


class SolanaHeliusGetNftEventsTool(BaseTool):
    name: str = "solana_helius_get_nft_events"
    description: str = """
    Fetch NFT events based on the given parameters.

    Input: A JSON string with:
    {
        "accounts": "List of addresses to fetch NFT events for",
        "types": "Optional list of event types",
        "sources": "Optional list of sources",
        "start_slot": "Optional start slot",
        "end_slot": "Optional end slot",
        "start_time": "Optional start time",
        "end_time": "Optional end time",
        "first_verified_creator": "Optional list of verified creators",
        "verified_collection_address": "Optional list of verified collection addresses",
        "limit": "Optional limit for results",
        "sort_order": "Optional sort order",
        "pagination_token": "Optional pagination token"
    }

    Output: {
        "events": List[dict], # list of NFT events matching the criteria
        "status": "success" or "error",
        "message": "Error message if any"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            accounts = data["accounts"]
            types = data.get("types")
            sources = data.get("sources")
            start_slot = data.get("start_slot")
            end_slot = data.get("end_slot")
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            first_verified_creator = data.get("first_verified_creator")
            verified_collection_address = data.get("verified_collection_address")
            limit = data.get("limit")
            sort_order = data.get("sort_order")
            pagination_token = data.get("pagination_token")

            result = await self.solana_kit.get_nft_events(
                accounts, types, sources, start_slot, end_slot, start_time, end_time, first_verified_creator, verified_collection_address, limit, sort_order, pagination_token
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")


class SolanaHeliusGetMintlistsTool(BaseTool):
    name: str = "solana_helius_get_mintlists"
    description: str = """
    Fetch mintlists for a given list of verified creators.

    Input: A JSON string with:
    {
        "first_verified_creators": "List of first verified creator addresses",
        "verified_collection_addresses": "Optional list of verified collection addresses",
        "limit": "Optional limit for results",
        "pagination_token": "Optional pagination token"
    }

    Output: {
        "mintlists": List[dict], # list of mintlists matching the criteria
        "status": "success" or "error",
        "message": "Error message if any"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            first_verified_creators = data["first_verified_creators"]
            verified_collection_addresses = data.get("verified_collection_addresses")
            limit = data.get("limit")
            pagination_token = data.get("pagination_token")

            result = await self.solana_kit.get_mintlists(first_verified_creators, verified_collection_addresses, limit, pagination_token)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")

class SolanaHeliusGetNFTFingerprintTool(BaseTool):
    name: str = "solana_helius_get_nft_fingerprint"
    description: str = """
    Fetch NFT fingerprint for a list of mint addresses.

    Input: A JSON string with:
    {
        "mints": ["string, the mint addresses of the NFTs"]
    }

    Output:
    {
        "fingerprint": "list of NFT fingerprint data"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            mints = data["mints"]

            result = await self.solana_kit.get_nft_fingerprint(mints)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaHeliusGetActiveListingsTool(BaseTool):
    name: str = "solana_helius_get_active_listings"
    description: str = """
    Fetch active NFT listings from various marketplaces.

    Input: A JSON string with:
    {
        "first_verified_creators": ["string, the addresses of verified creators"],
        "verified_collection_addresses": ["optional list of verified collection addresses"],
        "marketplaces": ["optional list of marketplaces"],
        "limit": "optional limit to the number of listings",
        "pagination_token": "optional token for pagination"
    }

    Output:
    {
        "active_listings": "list of active NFT listings"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            first_verified_creators = data["first_verified_creators"]
            verified_collection_addresses = data.get("verified_collection_addresses", [])
            marketplaces = data.get("marketplaces", [])
            limit = data.get("limit", None)
            pagination_token = data.get("pagination_token", None)

            result = await self.solana_kit.get_active_listings(
                first_verified_creators, verified_collection_addresses, marketplaces, limit, pagination_token
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaHeliusGetNFTMetadataTool(BaseTool):
    name: str = "solana_helius_get_nft_metadata"
    description: str = """
    Fetch metadata for NFTs based on their mint accounts.

    Input: A JSON string with:
    {
        "mint_accounts": ["string, the mint addresses of the NFTs"]
    }

    Output:
    {
        "metadata": "list of NFT metadata"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            mint_accounts = data["mint_accounts"]

            result = await self.solana_kit.get_nft_metadata(mint_accounts)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaHeliusGetRawTransactionsTool(BaseTool):
    name: str = "solana_helius_get_raw_transactions"
    description: str = """
    Fetch raw transactions for a list of accounts.

    Input: A JSON string with:
    {
        "accounts": ["string, the account addresses"],
        "start_slot": "optional start slot",
        "end_slot": "optional end slot",
        "start_time": "optional start time",
        "end_time": "optional end time",
        "limit": "optional limit",
        "sort_order": "optional sort order",
        "pagination_token": "optional pagination token"
    }

    Output:
    {
        "transactions": "list of raw transactions"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            accounts = data["accounts"]
            start_slot = data.get("start_slot", None)
            end_slot = data.get("end_slot", None)
            start_time = data.get("start_time", None)
            end_time = data.get("end_time", None)
            limit = data.get("limit", None)
            sort_order = data.get("sort_order", None)
            pagination_token = data.get("pagination_token", None)

            result = await self.solana_kit.get_raw_transactions(
                accounts, start_slot, end_slot, start_time, end_time, limit, sort_order, pagination_token
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaHeliusGetParsedTransactionsTool(BaseTool):
    name: str = "solana_helius_get_parsed_transactions"
    description: str = """
    Fetch parsed transactions for a list of transaction IDs.

    Input: A JSON string with:
    {
        "transactions": ["string, the transaction IDs"],
        "commitment": "optional commitment level"
    }

    Output:
    {
        "parsed_transactions": "list of parsed transactions"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            transactions = data["transactions"]
            commitment = data.get("commitment", None)

            result = await self.solana_kit.get_parsed_transactions(transactions, commitment)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )


class SolanaHeliusGetParsedTransactionHistoryTool(BaseTool):
    name: str = "solana_helius_get_parsed_transaction_history"
    description: str = """
    Fetch parsed transaction history for a given address.

    Input: A JSON string with:
    {
        "address": "string, the account address",
        "before": "optional before transaction timestamp",
        "until": "optional until transaction timestamp",
        "commitment": "optional commitment level",
        "source": "optional source of transaction",
        "type": "optional type of transaction"
    }

    Output:
    {
        "transaction_history": "list of parsed transaction history"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            address = data["address"]
            before = data.get("before", "")
            until = data.get("until", "")
            commitment = data.get("commitment", "")
            source = data.get("source", "")
            type = data.get("type", "")

            result = await self.solana_kit.get_parsed_transaction_history(
                address, before, until, commitment, source, type
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaHeliusCreateWebhookTool(BaseTool):
    name: str = "solana_helius_create_webhook"
    description: str = """
    Create a webhook for transaction events.

    Input: A JSON string with:
    {
        "webhook_url": "URL to send the webhook data",
        "transaction_types": "List of transaction types to listen for",
        "account_addresses": "List of account addresses to monitor",
        "webhook_type": "Type of webhook",
        "txn_status": "optional, transaction status to filter by",
        "auth_header": "optional, authentication header for the webhook"
    }

    Output:
    {
        "status": "success",
        "data": "Webhook creation response"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            webhook_url = data["webhook_url"]
            transaction_types = data["transaction_types"]
            account_addresses = data["account_addresses"]
            webhook_type = data["webhook_type"]
            txn_status = data.get("txn_status", "all")
            auth_header = data.get("auth_header", None)

            result = await self.solana_kit.create_webhook(
                webhook_url, transaction_types, account_addresses, webhook_type, txn_status, auth_header
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaHeliusGetAllWebhooksTool(BaseTool):
    name: str = "solana_helius_get_all_webhooks"
    description: str = """
    Fetch all webhooks created in the system.

    Input: None (No parameters required)

    Output:
    {
        "status": "success",
        "data": "List of all webhooks"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            result = await self.solana_kit.get_all_webhooks()
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaHeliusGetWebhookTool(BaseTool):
    name: str = "solana_helius_get_webhook"
    description: str = """
    Retrieve a specific webhook by ID.

    Input: A JSON string with:
    {
        "webhook_id": "ID of the webhook to retrieve"
    }

    Output:
    {
        "status": "success",
        "data": "Webhook details"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            webhook_id = data["webhook_id"]

            result = await self.solana_kit.get_webhook(webhook_id)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
class SolanaHeliusEditWebhookTool(BaseTool):
    name: str = "solana_helius_edit_webhook"
    description: str = """
    Edit an existing webhook by its ID.

    Input: A JSON string with:
    {
        "webhook_id": "ID of the webhook to edit",
        "webhook_url": "Updated URL for the webhook",
        "transaction_types": "Updated list of transaction types",
        "account_addresses": "Updated list of account addresses",
        "webhook_type": "Updated webhook type",
        "txn_status": "optional, updated transaction status filter",
        "auth_header": "optional, updated authentication header"
    }

    Output:
    {
        "status": "success",
        "data": "Updated webhook details"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            webhook_id = data["webhook_id"]
            webhook_url = data["webhook_url"]
            transaction_types = data["transaction_types"]
            account_addresses = data["account_addresses"]
            webhook_type = data["webhook_type"]
            txn_status = data.get("txn_status", "all")
            auth_header = data.get("auth_header", None)

            result = await self.solana_kit.edit_webhook(
                webhook_id, webhook_url, transaction_types, account_addresses, webhook_type, txn_status, auth_header
            )
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaHeliusDeleteWebhookTool(BaseTool):
    name: str = "solana_helius_delete_webhook"
    description: str = """
    Delete a webhook by its ID.

    Input: A JSON string with:
    {
        "webhook_id": "ID of the webhook to delete"
    }

    Output:
    {
        "status": "success",
        "data": "Webhook deletion confirmation"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            webhook_id = data["webhook_id"]

            result = await self.solana_kit.delete_webhook(webhook_id)
            return {
                "status": "success",
                "data": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """Synchronous version of the run method, required by BaseTool."""
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaFetchTokenReportSummaryTool(BaseTool):
    name: str = "solana_fetch_token_report_summary"
    description: str = """
    Fetch a summary report for a specific token.

    Input: A JSON string with:
    {
        "mint": "Mint address of the token"
    }

    Output:
    {
        "status": "success",
        "data": <TokenCheck object as a dictionary>
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        """
        Asynchronous implementation of the tool.
        """
        try:
            data = json.loads(input)
            mint = data.get("mint")
            if not mint:
                raise ValueError("Missing 'mint' in input.")
            
            result = self.solana_kit.fetch_token_report_summary(mint)
            return {
                "status": "success",
                "data": result.dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """
        Synchronous version of the tool, not implemented for async-only tools.
        """
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )
    
class SolanaFetchTokenDetailedReportTool(BaseTool):
    name: str = "solana_fetch_token_detailed_report"
    description: str = """
    Fetch a detailed report for a specific token.

    Input: A JSON string with:
    {
        "mint": "Mint address of the token"
    }

    Output:
    {
        "status": "success",
        "data": <TokenCheck object as a dictionary>
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        """
        Asynchronous implementation of the tool.
        """
        try:
            data = json.loads(input)
            mint = data.get("mint")
            if not mint:
                raise ValueError("Missing 'mint' in input.")
            
            result = self.solana_kit.fetch_token_detailed_report(mint)
            return {
                "status": "success",
                "data": result.dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        """
        Synchronous version of the tool, not implemented for async-only tools.
        """
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaGetPumpCurveStateTool(BaseTool):
    name: str = "solana_get_pump_curve_state"
    description: str = """
    Get the pump curve state for a specific bonding curve.

    Input: A JSON string with:
    {
        "conn": "AsyncClient instance or connection object",
        "curve_address": "The public key of the bonding curve as a string"
    }

    Output:
    {
        "status": "success",
        "data": <PumpCurveState object as a dictionary>
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            conn = data.get("conn")
            curve_address = data.get("curve_address")
            if not conn or not curve_address:
                raise ValueError("Missing 'conn' or 'curve_address' in input.")

            curve_address_key = Pubkey(curve_address)
            result = await self.solana_kit.get_pump_curve_state(conn, curve_address_key)
            return {
                "status": "success",
                "data": result.dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution.")

class SolanaCalculatePumpCurvePriceTool(BaseTool):
    name: str = "solana_calculate_pump_curve_price"
    description: str = """
    Calculate the price for a bonding curve based on its state.

    Input: A JSON string with:
    {
        "curve_state": "BondingCurveState object as a dictionary"
    }

    Output:
    {
        "status": "success",
        "price": "The calculated price"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            curve_state = data.get("curve_state")
            if not curve_state:
                raise ValueError("Missing 'curve_state' in input.")

            result = await self.solana_kit.calculate_pump_curve_price(curve_state)
            return {
                "status": "success",
                "price": result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution.")

class SolanaBuyTokenTool(BaseTool):
    name: str = "solana_buy_token"
    description: str = """
    Buy a specific amount of tokens using the bonding curve.

    Input: A JSON string with:
    {
        "mint": "The mint address of the token as a string",
        "bonding_curve": "The bonding curve public key as a string",
        "associated_bonding_curve": "The associated bonding curve public key as a string",
        "amount": "The amount of tokens to buy",
        "slippage": "The allowed slippage percentage",
        "max_retries": "Maximum retries for the transaction"
    }

    Output:
    {
        "status": "success",
        "transaction": "Details of the successful transaction"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            required_keys = ["mint", "bonding_curve", "associated_bonding_curve", "amount", "slippage", "max_retries"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing '{key}' in input.")

            mint = Pubkey(data["mint"])
            bonding_curve = Pubkey(data["bonding_curve"])
            associated_bonding_curve = Pubkey(data["associated_bonding_curve"])
            amount = data["amount"]
            slippage = data["slippage"]
            max_retries = data["max_retries"]

            result = await self.solana_kit.buy_token(
                mint, bonding_curve, associated_bonding_curve, amount, slippage, max_retries
            )
            return {
                "status": "success",
                "transaction": result.dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution.")

class SolanaSellTokenTool(BaseTool):
    name: str = "solana_sell_token"
    description: str = """
    Sell a specific amount of tokens using the bonding curve.

    Input: A JSON string with:
    {
        "mint": "The mint address of the token as a string",
        "bonding_curve": "The bonding curve public key as a string",
        "associated_bonding_curve": "The associated bonding curve public key as a string",
        "amount": "The amount of tokens to sell",
        "slippage": "The allowed slippage percentage",
        "max_retries": "Maximum retries for the transaction"
    }

    Output:
    {
        "status": "success",
        "transaction": "Details of the successful transaction"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            required_keys = ["mint", "bonding_curve", "associated_bonding_curve", "amount", "slippage", "max_retries"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing '{key}' in input.")

            mint = Pubkey(data["mint"])
            bonding_curve = Pubkey(data["bonding_curve"])
            associated_bonding_curve = Pubkey(data["associated_bonding_curve"])
            amount = data["amount"]
            slippage = data["slippage"]
            max_retries = data["max_retries"]

            result = await self.solana_kit.sell_token(
                mint, bonding_curve, associated_bonding_curve, amount, slippage, max_retries
            )
            return {
                "status": "success",
                "transaction": result.dict(),
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution.")

class SolanaSNSResolveTool(BaseTool):
    name: str = "solana_sns_resolve"
    description: str = """
    Resolves a Solana Name Service (SNS) domain to its corresponding address.

    Input: A JSON string with:
    {
        "domain": "string, the SNS domain (e.g., example.sol)"
    }

    Output:
    {
        "address": "string, the resolved Solana address",
        "message": "string, if resolution fails"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            domain = data["domain"]
            if not domain:
                raise ValueError("Domain is required.")

            address = await self.solana_kit.resolve_name_to_address(domain)
            return {
                "address": address or "Not Found",
                "message": "Success" if address else "Domain not found."
            }
        except Exception as e:
            return {
                "address": None,
                "message": f"Error resolving domain: {str(e)}"
            }

    def _run(self, input: str):
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaSNSRegisterDomainTool(BaseTool):
    name: str = "solana_sns_register_domain"
    description: str = """
    Prepares a transaction to register a new SNS domain.

    Input: A JSON string with:
    {
        "domain": "string, the domain to register",
        "buyer": "string, base58 public key of the buyer's wallet",
        "buyer_token_account": "string, base58 public key of the buyer's token account",
        "space": "integer, bytes to allocate for the domain",
        "mint": "string, optional, the token mint public key (default: USDC)",
        "referrer_key": "string, optional, base58 public key of the referrer"
    }

    Output:
    {
        "transaction": "string, base64-encoded transaction object",
        "message": "string, if an error occurs"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            domain = data["domain"]
            buyer = data["buyer"]
            buyer_token_account = data["buyer_token_account"]
            space = data["space"]
            mint = data.get("mint")
            referrer_key = data.get("referrer_key")

            if not all([domain, buyer, buyer_token_account, space]):
                raise ValueError("Domain, buyer, buyer_token_account, and space are required.")

            transaction = await self.solana_kit.get_registration_transaction(
                domain, buyer, buyer_token_account, space, mint, referrer_key
            )
            return {
                "transaction": transaction,
                "message": "Success"
            }
        except Exception as e:
            return {
                "transaction": None,
                "message": f"Error preparing registration transaction: {str(e)}"
            }

    def _run(self, input: str):
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaSNSGetFavouriteDomainTool(BaseTool):
    name: str = "solana_sns_get_favourite_domain"
    description: str = """
    Fetches the favorite domain of a given owner using Solana Name Service.

    Input: A JSON string with:
    {
        "owner": "string, the base58-encoded public key of the domain owner"
    }

    Output:
    {
        "domain": "string, the favorite domain of the owner",
        "message": "string, if an error occurs"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            owner = data["owner"]
            if not owner:
                raise ValueError("Owner address is required.")

            domain = await self.solana_kit.get_favourite_domain(owner)
            return {
                "domain": domain or "Not Found",
                "message": "Success" if domain else "No favorite domain found for this owner."
            }
        except Exception as e:
            return {
                "domain": None,
                "message": f"Error fetching favorite domain: {str(e)}"
            }

    def _run(self, input: str):
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaSNSGetAllDomainsTool(BaseTool):
    name: str = "solana_sns_get_all_domains"
    description: str = """
    Fetches all domains associated with a given owner using Solana Name Service.

    Input: A JSON string with:
    {
        "owner": "string, the base58-encoded public key of the domain owner"
    }

    Output:
    {
        "domains": ["string", "string", ...], # List of domains owned by the owner
        "message": "string, if an error occurs"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            owner = data["owner"]
            if not owner:
                raise ValueError("Owner address is required.")

            domains = await self.solana_kit.get_all_domains_for_owner(owner)
            return {
                "domains": domains or [],
                "message": "Success" if domains else "No domains found for this owner."
            }
        except Exception as e:
            return {
                "domains": [],
                "message": f"Error fetching domains: {str(e)}"
            }

    def _run(self, input: str):
        raise NotImplementedError(
            "This tool only supports async execution via _arun. Please use the async interface."
        )

class SolanaDeployCollectionTool(BaseTool):
    name: str = "solana_deploy_collection"
    description: str = """
    Deploys an NFT collection using the Metaplex program.

    Input: A JSON string with:
    {
        "name": "string, the name of the NFT collection",
        "uri": "string, the metadata URI",
        "royalty_basis_points": "int, royalty percentage in basis points (e.g., 500 for 5%)",
        "creator_address": "string, the creator's public key"
    }

    Output:
    {
        "success": "bool, whether the operation was successful",
        "value": "string, the transaction signature if successful",
        "message": "string, additional details or error information"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            name = data["name"]
            uri = data["uri"]
            royalty_basis_points = data["royalty_basis_points"]
            creator_address = data["creator_address"]

            if not all([name, uri, royalty_basis_points, creator_address]):
                raise ValueError("All input fields are required.")

            result = await self.solana_kit.deploy_collection(
                name=name,
                uri=uri,
                royalty_basis_points=royalty_basis_points,
                creator_address=creator_address,
            )
            return result
        except Exception as e:
            return {"success": False, "message": f"Error deploying collection: {str(e)}"}

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")

class SolanaGetMetaplexAssetTool(BaseTool):
    name: str = "solana_get_metaplex_asset"
    description: str = """
    Fetches detailed information about a specific Metaplex asset.

    Input: A JSON string with:
    {
        "asset_id": "string, the unique identifier of the asset"
    }

    Output:
    {
        "success": "bool, whether the operation was successful",
        "value": "object, detailed asset information if successful",
        "message": "string, additional details or error information"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            asset_id = data["asset_id"]

            if not asset_id:
                raise ValueError("Asset ID is required.")

            result = await self.solana_kit.get_metaplex_asset(asset_id)
            return result
        except Exception as e:
            return {"success": False, "message": f"Error fetching Metaplex asset: {str(e)}"}

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")
    
class SolanaGetMetaplexAssetsByCreatorTool(BaseTool):
    name: str = "solana_get_metaplex_assets_by_creator"
    description: str = """
    Fetches assets created by a specific creator.

    Input: A JSON string with:
    {
        "creator": "string, the creator's public key",
        "only_verified": "bool, fetch only verified assets (default: False)",
        "sort_by": "string, field to sort by (e.g., 'date')",
        "sort_direction": "string, 'asc' or 'desc'",
        "limit": "int, maximum number of assets",
        "page": "int, page number for paginated results"
    }

    Output:
    {
        "success": "bool, whether the operation was successful",
        "value": "list, the list of assets if successful",
        "message": "string, additional details or error information"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            creator = data["creator"]
            only_verified = data.get("only_verified", False)
            sort_by = data.get("sort_by")
            sort_direction = data.get("sort_direction")
            limit = data.get("limit")
            page = data.get("page")

            if not creator:
                raise ValueError("Creator address is required.")

            result = await self.solana_kit.get_metaplex_assets_by_creator(
                creator=creator,
                onlyVerified=only_verified,
                sortBy=sort_by,
                sortDirection=sort_direction,
                limit=limit,
                page=page,
            )
            return result
        except Exception as e:
            return {"success": False, "message": f"Error fetching assets by creator: {str(e)}"}

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")


class SolanaGetMetaplexAssetsByAuthorityTool(BaseTool):
    name: str = "solana_get_metaplex_assets_by_authority"
    description: str = """
    Fetches assets created by a specific authority.

    Input: A JSON string with:
    {
        "authority": "string, the authority's public key",
        "sort_by": "string, field to sort by (e.g., 'date')",
        "sort_direction": "string, 'asc' or 'desc'",
        "limit": "int, maximum number of assets",
        "page": "int, page number for paginated results"
    }

    Output:
    {
        "success": "bool, whether the operation was successful",
        "value": "list, the list of assets if successful",
        "message": "string, additional details or error information"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            authority = data["authority"]
            sort_by = data.get("sort_by")
            sort_direction = data.get("sort_direction")
            limit = data.get("limit")
            page = data.get("page")

            if not authority:
                raise ValueError("Creator address is required.")

            result = await self.solana_kit.get_metaplex_assets_by_authority(
                authority=authority,
                sortBy=sort_by,
                sortDirection=sort_direction,
                limit=limit,
                page=page,
            )
            return result
        except Exception as e:
            return {"success": False, "message": f"Error fetching assets by authority: {str(e)}"}

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")

class SolanaMintMetaplexCoreNFTTool(BaseTool):
    name: str = "solana_mint_metaplex_core_nft"
    description: str = """
    Mints an NFT using the Metaplex Core program.

    Input: A JSON string with:
    {
        "collection_mint": "string, the collection mint's public key",
        "name": "string, the name of the NFT",
        "uri": "string, the metadata URI",
        "seller_fee_basis_points": "int, royalty in basis points",
        "address": "string, the creator's public key",
        "share": "string, share percentage for the creator",
        "recipient": "string, recipient's public key"
    }

    Output:
    {
        "success": "bool, whether the operation was successful",
        "transaction": "string, the transaction signature if successful",
        "message": "string, additional details or error information"
    }
    """
    solana_kit: SolanaAgentKit

    async def _arun(self, input: str):
        try:
            data = json.loads(input)
            collection_mint = data["collection_mint"]
            name = data["name"]
            uri = data["uri"]
            seller_fee_basis_points = data.get("seller_fee_basis_points")
            address = data.get("address")
            share = data.get("share")
            recipient = data.get("recipient")

            if not all([collection_mint, name, uri]):
                raise ValueError("Collection mint, name, and URI are required.")

            result = await self.solana_kit.mint_metaplex_core_nft(
                collectionMint=collection_mint,
                name=name,
                uri=uri,
                sellerFeeBasisPoints=seller_fee_basis_points,
                address=address,
                share=share,
                recipient=recipient,
            )
            return result
        except Exception as e:
            return {"success": False, "message": f"Error minting NFT: {str(e)}"}

    def _run(self, input: str):
        raise NotImplementedError("This tool only supports async execution via _arun. Please use the async interface.")

def create_solana_tools(solana_kit: SolanaAgentKit):
    return [
        SolanaBalanceTool(solana_kit=solana_kit),
        SolanaTransferTool(solana_kit=solana_kit),
        SolanaDeployTokenTool(solana_kit=solana_kit),
        SolanaTradeTool(solana_kit=solana_kit),
        SolanaFaucetTool(solana_kit=solana_kit),
        SolanaStakeTool(solana_kit=solana_kit),
        SolanaPumpFunTokenTool(solana_kit=solana_kit),
        SolanaCreateImageTool(solana_kit=solana_kit),
        SolanaGetWalletAddressTool(solana_kit=solana_kit),
        SolanaTPSCalculatorTool(solana_kit=solana_kit),
        SolanaFetchPriceTool(solana_kit=solana_kit),
        SolanaTokenDataTool(solana_kit=solana_kit),
        SolanaTokenDataByTickerTool(solana_kit=solana_kit),
        SolanaMeteoraDLMMTool(solana_kit=solana_kit),
        SolanaRaydiumBuyTool(solana_kit=solana_kit),
        SolanaRaydiumSellTool(solana_kit=solana_kit),
        SolanaCreateGibworkTaskTool(solana_kit=solana_kit),
        SolanaSellUsingMoonshotTool(solana_kit=solana_kit),
        SolanaBuyUsingMoonshotTool(solana_kit=solana_kit),
        SolanaPythGetPriceTool(solana_kit=solana_kit),
        SolanaHeliusGetBalancesTool(solana_kit=solana_kit),
        SolanaHeliusGetAddressNameTool(solana_kit=solana_kit),
        SolanaHeliusGetNftEventsTool(solana_kit=solana_kit),
        SolanaHeliusGetMintlistsTool(solana_kit=solana_kit),
        SolanaHeliusGetNFTFingerprintTool(solana_kit=solana_kit),
        SolanaHeliusGetActiveListingsTool(solana_kit=solana_kit),
        SolanaHeliusGetNFTMetadataTool(solana_kit=solana_kit),
        SolanaHeliusGetRawTransactionsTool(solana_kit=solana_kit),
        SolanaHeliusGetParsedTransactionsTool(solana_kit=solana_kit),
        SolanaHeliusGetParsedTransactionHistoryTool(solana_kit=solana_kit),
        SolanaHeliusCreateWebhookTool(solana_kit=solana_kit),
        SolanaHeliusGetAllWebhooksTool(solana_kit=solana_kit),
        SolanaHeliusGetWebhookTool(solana_kit=solana_kit),
        SolanaHeliusEditWebhookTool(solana_kit=solana_kit),
        SolanaHeliusDeleteWebhookTool(solana_kit=solana_kit),
        SolanaFetchTokenReportSummaryTool(solana_kit=solana_kit),
        SolanaFetchTokenDetailedReportTool(solana_kit=solana_kit),
        SolanaGetPumpCurveStateTool(solana_kit=solana_kit),
        SolanaCalculatePumpCurvePriceTool(solana_kit=solana_kit),
        SolanaBuyTokenTool(solana_kit=solana_kit),
        SolanaSellTokenTool(solana_kit=solana_kit),
        SolanaSNSGetAllDomainsTool(solana_kit=solana_kit),
        SolanaSNSRegisterDomainTool(solana_kit=solana_kit),
        SolanaSNSGetFavouriteDomainTool(solana_kit=solana_kit),
        SolanaSNSResolveTool(solana_kit=solana_kit),
        SolanaGetMetaplexAssetsByAuthorityTool(solana_kit=solana_kit),
        SolanaGetMetaplexAssetsByCreatorTool(solana_kit=solana_kit),
        SolanaGetMetaplexAssetTool(solana_kit=solana_kit),
        SolanaMintMetaplexCoreNFTTool(solana_kit=solana_kit),
        SolanaDeployCollectionTool(solana_kit=solana_kit),
    ]


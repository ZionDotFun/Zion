import json

from langchain.tools import BaseTool
from solders.pubkey import Pubkey  # type: ignore

from agentipy.agent import SolanaAgentKit
from agentipy.tools import create_image, fetch_price
from agentipy.utils import toJSON


class SolanaBalanceTool(BaseTool):
    name:str = "solana_balance"
    description:str = """
    Get the balance of a Solana wallet or token account.

    If you want to get the balance of your wallet, you don't need to provide the tokenAddress.
    If no tokenAddress is provided, the balance will be in SOL.
    """

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

class SolanaDeployTokenTool(BaseTool):
    name:str = "solana_deploy_token"
    description:str = """
    Deploy a new SPL token. Input should be JSON string with:
    {
        "decimals": 9,
        "initialSupply": 1000
    }
    """

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

class SolanaFaucetTool(BaseTool):
    name:str = "solana_request_funds"
    description:str = "Request test funds from a Solana faucet."

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

class SolanaStakeTool(BaseTool):
    name:str = "solana_stake"
    description:str = "Stake assets on Solana. Input is the amount to stake."

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

class SolanaGetWalletAddressTool(BaseTool):
    name:str = "solana_get_wallet_address"
    description:str = "Get the wallet address of the agent"

    def __init__(self, solana_kit:SolanaAgentKit):
        self.solana_kit = solana_kit
    
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

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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

class SolanaTPSCalculatorTool(BaseTool):
    name: str = "solana_get_tps"
    description: str = "Get the current TPS of the Solana network."

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

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
class SolanaPumpFunTokenTool(BaseTool):
    nam:str = "solana_launch_pump_fun_token"
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

    def __init__(self, solana_kit: SolanaAgentKit):
        self.solana_kit = solana_kit

    async def _arun(self, input: str):
        try:
            data = toJSON(input)
            result = await self.solana_kit.launch_pump_fun_token(
                data["token_name"],
                data["token_ticker"],
                data["description"],
                data["image_url"],
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

class SolanaFetchPriceTool(BaseTool):
    """
    Tool to fetch the price of a token in USDC.
    """
    name:str = "solana_fetch_price"
    description:str = """Fetch the price of a given token in USDC.

    Inputs:
    - tokenId: string, the mint address of the token, e.g., "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN"
    """

    def __init__(self, solana_kit):
        self.solana_kit = solana_kit

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


class SolanaTokenDataTool(BaseTool):
    """
    Tool to fetch token data for a given token mint address.
    """
    name:str = "solana_token_data"
    description:str = """Get the token data for a given token mint address.

    Inputs:
    - mintAddress: string, e.g., "So11111111111111111111111111111111111111112" (required)
    """

    def __init__(self, solana_kit):
        self.solana_kit = solana_kit

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


class SolanaTokenDataByTickerTool(BaseTool):
    """
    Tool to fetch token data for a given token ticker.
    """
    name:str = "solana_token_data_by_ticker"
    description:str = """Get the token data for a given token ticker.

    Inputs:
    - ticker: string, e.g., "USDC" (required)
    """

    def __init__(self, solana_kit):
        self.solana_kit = solana_kit

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
        
def create_solana_tools(solana_kit: SolanaAgentKit):
    return [
        SolanaBalanceTool(solana_kit),
        SolanaTransferTool(solana_kit),
        SolanaDeployTokenTool(solana_kit),
        SolanaTradeTool(solana_kit),
        SolanaFaucetTool(solana_kit),
        SolanaStakeTool(solana_kit),
        SolanaPumpFunTokenTool(solana_kit),
        SolanaCreateImageTool(solana_kit),
        SolanaGetWalletAddressTool(solana_kit),
        SolanaTPSCalculatorTool(solana_kit),
        SolanaFetchPriceTool(solana_kit),
        SolanaTokenDataTool(solana_kit),
        SolanaTokenDataByTickerTool(solana_kit)
    ]

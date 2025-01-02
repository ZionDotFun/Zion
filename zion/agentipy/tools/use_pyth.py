import asyncio

from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.solana import (PYTHNET_HTTP_ENDPOINT, PYTHNET_WS_ENDPOINT,
                               SolanaClient, SolanaPublicKey)


class PythManager:
    @staticmethod
    async def get_price(mint_address: str):
        """
        Fetch price data for a given token mint address using the Pyth Oracle.

        :param mint_address: The mint address of the token.
        :return: A dictionary containing the price and confidence interval.
        """
        account_key = SolanaPublicKey(mint_address)
        solana_client = SolanaClient(endpoint=PYTHNET_HTTP_ENDPOINT, ws_endpoint=PYTHNET_WS_ENDPOINT)
        price = PythPriceAccount(account_key, solana_client)

        await price.update()

        price_status = price.aggregate_price_status
        if price_status == PythPriceStatus.TRADING:
            result = {
                "price": price.aggregate_price,
                "confidence_interval": price.aggregate_price_confidence_interval,
                "status": "TRADING",
            }
        else:
            result = {
                "status": "NOT_TRADING",
                "message": f"Price is not valid now. Status is {price_status}",
            }

        await solana_client.close()
        return result

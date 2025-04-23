import logging

import requests

from agentipy.types import TokenCheck

BASE_URL = "https://api.rugcheck.xyz/v1"

logger = logging.getLogger(__name__)

class RugCheckManager:
    @staticmethod

    def fetch_token_report_summary(mint: str) -> TokenCheck:
        """
        Fetches a summary report for a specific token.
        
        Args:
            mint (str): The mint address of the token.

        Returns:
            TokenCheck: The token summary report.

        Raises:
            Exception: If the API call fails.
        """

        try:
            response = requests.get(f"{BASE_URL}/tokens/{mint}/report/summary")
            response.raise_for_status()
            return TokenCheck(**response.json())
        except requests.RequestException as error:
            logger.info(f"Error fetching report summary for token {mint}: {error}")
            raise Exception(f"Failed to fetch report summary for token {mint}") from error
    @staticmethod
    def fetch_token_detailed_report(mint:str) -> TokenCheck:
        """
        Fetches a detailed report for a specific token.
        
        Args:
            mint (str): The mint address of the token.

        Returns:
            TokenCheck: The detailed token report.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = requests.get(f"{BASE_URL}/tokens/{mint}/report")
            response.raise_for_status()
            return TokenCheck(**response.json())
        except requests.RequestException as error:
            logger.info(f"Error fetching detailed report for token {mint}: {error}")
            raise Exception(f"Failed to fetch detailed report for token {mint}.") from error

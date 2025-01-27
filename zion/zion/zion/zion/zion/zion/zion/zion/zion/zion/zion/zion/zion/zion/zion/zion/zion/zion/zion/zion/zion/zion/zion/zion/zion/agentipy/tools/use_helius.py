from typing import List

from agentipy.agent import SolanaAgentKit
from agentipy.utils.helius.helpers.utility import (_make_delete_request,
                                                   _make_get_request,
                                                   _make_post_request,
                                                   _make_put_request)


class HeliusManager:
    def __init__(self, agent:SolanaAgentKit):
        self.base_url = agent.helius_rpc_url
        self.api_key_query = f"?api-key={agent.helius_api_key}"

    def get_balances(self, address: str):
        path = f"/v0/addresses/{address}/balances"
        url = self.base_url + path + self.api_key_query
        return _make_get_request(url)
    
    def get_address_name(self, address: str):
        path = f"/v0/addresses/{address}/names"
        url = self.base_url + path + self.api_key_query
        return _make_get_request(url)
    
    def get_nft_events(
            self,
            accounts: List[str],
            types: List[str] = None,
            sources: List[str] = None,
            start_slot: int = None,
            end_slot: int = None,
            start_time: int = None,
            end_time: int = None,
            first_verified_creator: List[str] = None,
            verified_collection_address: List[str] = None,
            limit : int = None,
            sort_order: str = None,
            pagination_token: str = None
    ):
        path = "/v1/nft-events"
        url = self.base_url + path + self.api_key_query
        payload = {
            "query": {
                "accounts": accounts,
                "types": types,
                "sources": sources,
                "startSlot": start_slot,
                "endSlot": end_slot,
                "startTime": start_time,
                "endTime": end_time,
                "nftCollectionFilters": {
                    "firstVerifiedCreator": first_verified_creator,
                    "verifiedCollectionAddress": verified_collection_address
                }
            },
            "options": {
                "limit":limit,
                "sortOrder": sort_order,
                "paginationToken": pagination_token
            }
        }
        return _make_post_request(url,payload)
    
    def get_mintlists(
        self, 
        first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        limit: int=None,
        pagination_token: str=None
        ):

        path = "/v1/mintlist"
        url = self.base_url + path + self.api_key_query
        payload = {
            "query": {
                "firstVerifiedCreators": first_verified_creators,
                "verifiedCollectionAddresses": verified_collection_addresses
            },
            "options": {
                "limit": limit,
                "paginationToken": pagination_token
            }
        }
        return _make_post_request(url, payload)

    def get_nft_fingerprint(self, mints: List[str]):
        path = "/v1/nfts"
        url = self.base_url + path + self.api_key_query
        payload = {
            "mints": mints
        }
        return _make_post_request(url, payload)

    def get_active_listings(
        self, 
        first_verified_creators: List[str],
        verified_collection_addresses: List[str]=None,
        marketplaces: List[str]=None,
        limit: int=None,
        pagination_token: str=None
        ):

        path = "/v1/active-listings"
        url = self.base_url + path + self.api_key_query
        payload = {
            "query": {
                "marketplaces": marketplaces,
                "firstVerifiedCreators": first_verified_creators,
                "verifiedCollectionAddresses": verified_collection_addresses
            },
            "options": {
                "limit": limit,
                "paginationToken": pagination_token
            }
        }
        return _make_post_request(url, payload)

    def get_nft_metadata(self, mint_accounts: List[str]):
        path = "/v0/tokens/metadata"
        url = self.base_url + path + self.api_key_query
        payload = {
            "mintAccounts": mint_accounts
        }
        return _make_post_request(url, payload)
        
    def get_raw_transactions(
        self, 
        accounts: List[str], 
        start_slot: int=None,
        end_slot: int=None,
        start_time: int=None,
        end_time: int=None,
        limit: int=None,
        sort_order: str=None,
        pagination_token: str=None
        ):

        path = "/v1/raw-transactions"
        url = self.base_url + path + self.api_key_query
        payload = {
            "query": {
                "accounts": accounts,
                "startSlot": start_slot,
                "endSlot": end_slot,
                "startTime": start_time,
                "endTime": end_time
            },
            "options": {
                "limit": limit,
                "sortOrder": sort_order,
                "paginationToken": pagination_token
            }
        }
        return _make_post_request(url, payload)

    def get_parsed_transactions(self, transactions: List[str], commitment: str=None):
        path = "/v0/transactions"
        if commitment:
            url = self.base_url + path + self.api_key_query + "?commitment=commitment"
        else:
            url = self.base_url + path + self.api_key_query
        payload = {
            "transactions": transactions
        }
        return _make_post_request(url, payload)

    def get_parsed_transaction_history(
        self, 
        address: str, 
        before: str='', 
        until: str='', 
        commitment: str='',
        source: str='',
        type: str=''
        ):
        
        path = f"/v0/addresses/{address}/transactions"
        params = {
            "before": before,
            "until": until,
            "commitment": commitment,
            "source": source,
            "type": type
        }

        url = self.base_url + path + self.api_key_query
        return _make_get_request(url, params=params)
    
    def create_webhook(
        self, 
        webhook_url: str, 
        transaction_types: list, 
        account_addresses: list, 
        webhook_type: str, 
        txn_status: str="all",
        auth_header: str=None
        ):
        
        path = "/v0/webhooks"
        url = self.base_url + path + self.api_key_query
        payload = {
            "webhookURL": webhook_url,
            "transactionTypes": transaction_types,
            "accountAddresses": account_addresses,
            "webhookType": webhook_type,
            "txnStatus": txn_status
        }
        if auth_header:
            payload["authHeader"] = auth_header

        return _make_post_request(url, payload)

    def get_all_webhooks(self):
        path = "/v0/webhooks"
        url = self.base_url + path + self.api_key_query

        return _make_get_request(url)

    def get_webhook(self, webhook_id: str):
        path = f"/v0/webhooks/{webhook_id}"
        url = self.base_url + path + self.api_key_query

        return _make_get_request(url)

    def edit_webhook(
        self, 
        webhook_id: str, 
        webhook_url: str, 
        transaction_types: list, 
        account_addresses: list, 
        webhook_type: str, 
        txn_status: str="all",
        auth_header: str=None
        ):

        path = f"/v0/webhooks/{webhook_id}"
        url = self.base_url + path + self.api_key_query
        payload = {
            "webhookURL": webhook_url,
            "transactionTypes": transaction_types,
            "accountAddresses": account_addresses,
            "webhookType": webhook_type,
            "txnStatus": txn_status
        }
    
        if auth_header:
            payload["authHeader"] = auth_header

        return _make_put_request(url, payload)

    def delete_webhook(self, webhook_id: str):
        path = f"/v0/webhooks/{webhook_id}"
        url = self.base_url + path + self.api_key_query
        
        return _make_delete_request(url)
from agentipy.agent import SolanaAgentKit
from agentipy.utils.jito import __send_request

import random

class JitoManager:
    #Bundle Endpoint
    def get_tip_accounts(agent: SolanaAgentKit):
        if agent.jito_uuid == None:
            return __send_request(agent, endpoint="/bundles", method="getTipAccounts")
        else:
            return __send_request(agent, endpoint="/bundles?uuid=" + agent.jito_uuid, method="getTipAccounts")

    def get_random_tip_account(self):
        response = self.get_tip_accounts()
        if not response['success']:
            print(f"Error getting tip accounts: {response.get('error', 'Unknown error')}")
            return None
        
        tip_accounts = response['data']['result']
        if not tip_accounts:
            print("No tip accounts found.")
            return None
        
        random_account = random.choice(tip_accounts)
        return random_account

    def get_bundle_statuses(agent: SolanaAgentKit, bundle_uuids):
        endpoint = "/bundles"
        if agent.jito_uuid is not None:
            endpoint += f"?uuid={agent.jito_uuid}"
        
        # Ensure bundle_uuids is a list
        if not isinstance(bundle_uuids, list):
            bundle_uuids = [bundle_uuids]
        
        # Correct format for the request
        params = bundle_uuids
        
        return __send_request(agent, endpoint=endpoint, method="getBundleStatuses", params=params)

    def send_bundle(agent: SolanaAgentKit, params=None):
        if agent.jito_uuid == None:
            return __send_request(agent, endpoint="/bundles",method="sendBundle", params=params)
        else:
            return  __send_request(agent, endpoint="/bundles?uuid=" + agent.jito_uuid, method="sendBundle", params=params)

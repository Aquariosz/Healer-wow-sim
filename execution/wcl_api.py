import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WCL_CLIENT_ID = os.getenv("WCL_CLIENT_ID")
WCL_CLIENT_SECRET = os.getenv("WCL_CLIENT_SECRET")
TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"
GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/client"

class WarcraftLogsAPI:
    def __init__(self):
        self.client_id = WCL_CLIENT_ID
        self.client_secret = WCL_CLIENT_SECRET
        self.access_token = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates with the WCL API and retrieves an OAuth token."""
        if not self.client_id or not self.client_secret:
            raise ValueError("WCL_CLIENT_ID and WCL_CLIENT_SECRET must be set in the .env file.")

        response = requests.post(
            TOKEN_URL,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"}
        )

        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
        else:
            raise Exception(f"Failed to authenticate with WCL API: {response.status_code} - {response.text}")

    def query(self, graphql_query: str, variables: dict = None):
        """Executes a GraphQL query against the WCL API."""
        if not self.access_token:
            self._authenticate()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": graphql_query}
        if variables:
            payload["variables"] = variables

        response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Token might have expired, re-authenticate and try again
            self._authenticate()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.post(GRAPHQL_URL, headers=headers, json=payload)
            if response.status_code == 200:
                 return response.json()
                 
        raise Exception(f"GraphQL Query failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Test the connection (will fail if client_secret is empty, which is expected for now)
    try:
        api = WarcraftLogsAPI()
        print("Successfully authenticated with Warcraft Logs API!")
    except Exception as e:
        print(f"Authentication test failed: {e}")

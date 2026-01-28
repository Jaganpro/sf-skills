"""
JWT Bearer authentication for Salesforce Data Cloud.

Uses certificate patterns from sf-connected-apps skill for secure
server-to-server authentication without user interaction.

Prerequisites (via sf-connected-apps skill):
1. Generate certificate: openssl req -x509 -sha256 -nodes ...
2. Create External Client App with JWT Bearer flow
3. Upload certificate to Salesforce
4. Store private key at ~/.sf/jwt/{org_alias}.key

Usage:
    auth = DataCloudAuth(org_alias="myorg", consumer_key="3MVG9...")
    token = auth.get_token()
    # Use token for Data Cloud API requests
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import jwt
import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


# Default paths for JWT keys
DEFAULT_KEY_DIR = Path.home() / ".sf" / "jwt"

# Salesforce OAuth endpoints
LOGIN_URL = "https://login.salesforce.com"
TEST_LOGIN_URL = "https://test.salesforce.com"

# Token refresh buffer (refresh 5 minutes before expiry)
TOKEN_REFRESH_BUFFER = 300


@dataclass
class OrgInfo:
    """Salesforce org connection information."""

    instance_url: str
    username: str
    access_token: Optional[str] = None
    is_sandbox: bool = False

    @property
    def login_url(self) -> str:
        """Get the appropriate login URL based on org type."""
        return TEST_LOGIN_URL if self.is_sandbox else LOGIN_URL


@dataclass
class DataCloudAuth:
    """
    JWT Bearer authentication for Data Cloud Query API.

    This class handles:
    - JWT assertion generation using X.509 certificates
    - Token exchange with Salesforce OAuth endpoint
    - Token caching and automatic refresh
    - Integration with sf CLI for org discovery

    Attributes:
        org_alias: Salesforce CLI org alias
        consumer_key: Connected App consumer key (client ID)
        key_path: Path to private key file (default: ~/.sf/jwt/{org_alias}.key)

    Example:
        >>> auth = DataCloudAuth("prod", "3MVG9...")
        >>> token = auth.get_token()
        >>> headers = {"Authorization": f"Bearer {token}"}
    """

    org_alias: str
    consumer_key: str
    key_path: Optional[Path] = None
    _token: Optional[str] = field(default=None, repr=False)
    _token_expiry: float = field(default=0, repr=False)
    _org_info: Optional[OrgInfo] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize key path if not provided."""
        if self.key_path is None:
            self.key_path = DEFAULT_KEY_DIR / f"{self.org_alias}.key"

    @property
    def org_info(self) -> OrgInfo:
        """Get org information from sf CLI (cached)."""
        if self._org_info is None:
            self._org_info = self._get_org_info()
        return self._org_info

    def _get_org_info(self) -> OrgInfo:
        """
        Retrieve org information using sf CLI.

        Returns:
            OrgInfo with instance URL and username

        Raises:
            RuntimeError: If sf CLI command fails
        """
        try:
            result = subprocess.run(
                ["sf", "org", "display", "--target-org", self.org_alias, "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)

            if data.get("status") != 0:
                raise RuntimeError(f"sf org display failed: {data.get('message', 'Unknown error')}")

            result_data = data.get("result", {})
            instance_url = result_data.get("instanceUrl", "")
            username = result_data.get("username", "")
            is_sandbox = result_data.get("isSandbox", False) or "sandbox" in instance_url.lower()

            return OrgInfo(
                instance_url=instance_url,
                username=username,
                is_sandbox=is_sandbox
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get org info: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse sf CLI output: {e}")

    def _load_private_key(self) -> bytes:
        """
        Load private key from file.

        Returns:
            Private key bytes

        Raises:
            FileNotFoundError: If key file doesn't exist
        """
        if not self.key_path.exists():
            raise FileNotFoundError(
                f"Private key not found at {self.key_path}\n"
                f"Generate with: openssl req -x509 -sha256 -nodes -days 365 "
                f"-newkey rsa:2048 -keyout {self.key_path} -out {self.key_path.with_suffix('.crt')}"
            )

        return self.key_path.read_bytes()

    def _create_jwt_assertion(self) -> str:
        """
        Create a signed JWT assertion for the OAuth flow.

        The JWT includes:
        - iss: Consumer key (client ID)
        - sub: Salesforce username
        - aud: Login URL
        - exp: Expiration time (5 minutes from now)

        Returns:
            Signed JWT string
        """
        private_key_bytes = self._load_private_key()

        # Load the private key
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )

        # Create JWT payload
        now = int(time.time())
        payload = {
            "iss": self.consumer_key,
            "sub": self.org_info.username,
            "aud": self.org_info.login_url,
            "exp": now + 300,  # 5 minute expiry
        }

        # Sign and return
        return jwt.encode(payload, private_key, algorithm="RS256")

    def _exchange_token(self, assertion: str) -> dict:
        """
        Exchange JWT assertion for access token.

        Args:
            assertion: Signed JWT assertion

        Returns:
            Token response dict with access_token, instance_url, etc.

        Raises:
            RuntimeError: If token exchange fails
        """
        token_url = f"{self.org_info.login_url}/services/oauth2/token"

        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }

        with httpx.Client() as client:
            response = client.post(token_url, data=data)

            if response.status_code != 200:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error_description", response.text)
                raise RuntimeError(f"Token exchange failed: {error_msg}")

            return response.json()

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get or refresh the access token.

        Tokens are cached and automatically refreshed before expiry.

        Args:
            force_refresh: Force token refresh even if current token is valid

        Returns:
            Valid access token string

        Example:
            >>> auth = DataCloudAuth("prod", "3MVG9...")
            >>> token = auth.get_token()
            >>> # Token is cached, subsequent calls are fast
            >>> token = auth.get_token()  # Returns cached token
        """
        # Check if current token is still valid
        if not force_refresh and self._token and time.time() < self._token_expiry:
            return self._token

        # Generate new JWT assertion
        assertion = self._create_jwt_assertion()

        # Exchange for access token
        token_response = self._exchange_token(assertion)

        self._token = token_response["access_token"]
        # Salesforce tokens typically expire in 1-2 hours; refresh 5 min early
        self._token_expiry = time.time() + 3600 - TOKEN_REFRESH_BUFFER

        # Update instance URL if different
        if token_response.get("instance_url"):
            self._org_info = OrgInfo(
                instance_url=token_response["instance_url"],
                username=self.org_info.username,
                is_sandbox=self.org_info.is_sandbox
            )

        return self._token

    def get_headers(self) -> dict:
        """
        Get HTTP headers with valid authorization.

        Returns:
            Dict with Authorization header

        Example:
            >>> auth = DataCloudAuth("prod", "3MVG9...")
            >>> headers = auth.get_headers()
            >>> response = httpx.get(url, headers=headers)
        """
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }

    @property
    def instance_url(self) -> str:
        """Get the Salesforce instance URL."""
        return self.org_info.instance_url

    def test_connection(self) -> bool:
        """
        Test the authentication by making a simple API call.

        Returns:
            True if authentication is successful

        Raises:
            RuntimeError: If authentication fails
        """
        token = self.get_token()

        # Test with a simple Data Cloud metadata call
        url = f"{self.instance_url}/services/data/v60.0/ssot/querybuilder/metadata"

        with httpx.Client() as client:
            response = client.get(url, headers=self.get_headers())

            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                raise RuntimeError("Authentication failed: Invalid or expired token")
            elif response.status_code == 403:
                raise RuntimeError(
                    "Access denied: Ensure ECA has cdp_query_api scope and user has Data Cloud permissions"
                )
            else:
                raise RuntimeError(f"Connection test failed: {response.status_code} - {response.text}")


def get_auth_from_env(org_alias: str) -> DataCloudAuth:
    """
    Create DataCloudAuth from environment variables.

    Expects:
    - SF_CONSUMER_KEY or SF_{ORG_ALIAS}_CONSUMER_KEY environment variable
    - Private key at ~/.sf/jwt/{org_alias}.key

    Args:
        org_alias: Salesforce org alias

    Returns:
        Configured DataCloudAuth instance
    """
    import os

    # Try org-specific key first, then generic
    consumer_key = os.environ.get(f"SF_{org_alias.upper()}_CONSUMER_KEY")
    if not consumer_key:
        consumer_key = os.environ.get("SF_CONSUMER_KEY")

    if not consumer_key:
        raise ValueError(
            f"Consumer key not found. Set SF_CONSUMER_KEY or SF_{org_alias.upper()}_CONSUMER_KEY"
        )

    return DataCloudAuth(org_alias=org_alias, consumer_key=consumer_key)

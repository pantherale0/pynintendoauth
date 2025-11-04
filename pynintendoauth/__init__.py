"""Base Nintendo authentication library."""

import logging

from datetime import datetime, timedelta

from urllib.parse import urlencode

import aiohttp

from .const import (
    AUTHORIZE_URL,
    TOKEN_URL,
    GRANT_TYPE,
    MY_ACCOUNT_ENDPOINT,
    SESSION_TOKEN_URL,
    KNOWN_NINTENDO_SERVICES
)

from .exceptions import (
    HttpException,
    InvalidOAuthConfigurationException,
    InvalidSessionTokenException,
)
from .utils import gen_rand, calc_hash, parse_response_token

_LOGGER = logging.getLogger(__name__)


class NintendoAuth:
    """Authentication functions."""

    def __init__(
        self,
        client_id: str,
        scopes: list[str] | None = None,
        redirect_url: str | None = None,
        session_token: str | None = None,
        client_session: aiohttp.ClientSession | None = None,
    ):
        """Basic auth init."""
        _LOGGER.debug(">> Init authenticator.")
        if scopes is None:
            if client_id not in KNOWN_NINTENDO_SERVICES:
                raise ValueError("Client ID not known by this module.")
            scopes = KNOWN_NINTENDO_SERVICES[client_id]["scopes"]
            redirect_url = KNOWN_NINTENDO_SERVICES[client_id]["redirect_url"]
        self._client_id = client_id
        self._scopes = scopes
        self._redirect_url = redirect_url
        self._at_expiry: datetime = None
        self._access_token: str = None
        self.available_scopes: dict = None
        self.account: dict = None
        self._refresh_token: str = None
        self._id_token: str = None
        self._session_token: str | None = session_token
        self.login_url: str = None
        if client_session is None:
            client_session = aiohttp.ClientSession()
        self.client_session: aiohttp.ClientSession = client_session
        if self._session_token is None:
            self._generate_login()

    def _generate_login(self):
        """Generate initial login data."""
        verifier = gen_rand()
        query = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_url,
            "response_type": "session_token_code",
            "scope": "+".join(self._scopes),
            "session_token_code_challenge": calc_hash(verifier),
            "session_token_code_challenge_method": "S256",
            "state": gen_rand(),
            "theme": "login_form",
        }
        self.login_url = AUTHORIZE_URL.format(urlencode(query).replace("%2B", "+"))
        self._auth_code_verifier = verifier

    async def _request_handler(
        self, method, url, json=None, data=None, headers: dict = None
    ) -> aiohttp.ClientResponse:
        """Send a HTTP request"""
        if headers is None:
            headers = {}
        return await self.client_session.request(
            method=method, url=url, json=json, data=data, headers=headers
        )

    async def _perform_refresh(self):
        """Refresh the access token."""
        _LOGGER.debug("Refreshing access token.")
        token_response = await self._request_handler(
            method="POST",
            url=TOKEN_URL,
            json={
                "client_id": self._client_id,
                "grant_type": GRANT_TYPE,
                "session_token": self._session_token,
            },
        )

        response_body = await token_response.json()
        if not token_response.ok:
            if token_response.status == 400:
                raise InvalidSessionTokenException(400, response_body["error"])

            if token_response.status == 401:
                raise InvalidOAuthConfigurationException(401, response_body["error"])

            if token_response.status != 200:
                raise HttpException(
                    token_response.status, f"login error {token_response.status}"
                )

        self._read_tokens(response_body)
        if self.account_id is None:
            # fill account_id
            account = await self._request_handler(
                method="GET",
                url=MY_ACCOUNT_ENDPOINT,
                headers={"Authorization": f"Bearer {self._access_token}"},
            )
            if not account.ok:
                raise HttpException(
                    account.status, f"Unable to get account_id {account.status}"
                )
            response_body = await account.json()
            self.account = response_body

    async def _perform_login(self, session_token_code):
        """Retrieves initial tokens."""
        _LOGGER.debug("Performing initial login.")
        session_token_form = aiohttp.FormData()
        session_token_form.add_field("client_id", self._client_id)
        session_token_form.add_field("session_token_code", session_token_code)
        session_token_form.add_field(
            "session_token_code_verifier", self._auth_code_verifier
        )
        session_token_response = await self._request_handler(
            method="POST", url=SESSION_TOKEN_URL, data=session_token_form
        )

        if not session_token_response.ok:
            raise HttpException(
                session_token_response.status, await session_token_response.text()
            )
        data = await session_token_response.json()
        self._session_token = data["session_token"]

    async def async_complete_login(
        self, response_token: str | None = None, use_session_token: bool = False
    ):
        """Complete Nintendo Online login process."""
        if use_session_token and self._session_token is not None:
            await self._perform_refresh()
            return
        if response_token is None:
            raise ValueError("Response token must not be null if not using an existing session token.")
        response_token = parse_response_token(response_token)
        await self._perform_login(
            session_token_code=response_token.get("session_token_code")
        )
        await self._perform_refresh()

    async def async_authenticated_request(
        self,
        method: str,
        url: str,
        headers: dict,
        body: dict | None = None,
    ) -> aiohttp.ClientResponse:
        """Send a authenticated request to a given URL."""
        if self.access_token_expired:
            await self._perform_refresh()
        if method not in aiohttp.ClientRequest.ALL_METHODS:
            raise ValueError("Invalid request method.")
        return await self.client_session.request(
            method=method,
            url=url,
            headers={
                **headers,
                "Authorization": self.access_token,
            },
            json=body
        )

    @property
    def account_id(self) -> str | None:
        """Return account ID."""
        if self.account is None:
            return
        if "id" not in self.account:
            return
        return self.account["id"]

    @property
    def session_token(self) -> str:
        """Return the session token."""
        return self._session_token

    @property
    def access_token(self) -> str:
        """Return the formatted access token."""
        return f"Bearer {self._id_token}"

    @property
    def access_token_expired(self) -> bool:
        """Check if the access token has expired."""
        return self._at_expiry < (datetime.now() + timedelta(minutes=1))

    def _read_tokens(self, tokens: dict):
        """Reads tokens into self."""
        self.available_scopes = tokens.get("scope")
        self._at_expiry = datetime.now() + timedelta(seconds=tokens.get("expires_in"))
        self._id_token = tokens.get("id_token")
        self._access_token = tokens.get("access_token")

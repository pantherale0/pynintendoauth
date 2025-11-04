"""Nintendo Auth consts."""

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token"
AUTHORIZE_URL = "https://accounts.nintendo.com/connect/1.0.0/authorize?{}"
SESSION_TOKEN_URL = "https://accounts.nintendo.com/connect/1.0.0/api/session_token"
TOKEN_URL = "https://accounts.nintendo.com/connect/1.0.0/api/token"

ACCOUNT_API_BASE = "https://api.accounts.nintendo.com/2.0.0"
MY_ACCOUNT_ENDPOINT = f"{ACCOUNT_API_BASE}/users/me"

DEFAULT_SCOPES = [
    "openid",
    "user"
]


KNOWN_NINTENDO_SERVICES = {
    "54789befb391a838": {
        "redirect_url": "npf54789befb391a838://auth",
        "scopes": [
            *DEFAULT_SCOPES,
            "moonUser:administration",
            "moonDevice:create",
            "moonOwnedDevice:administration",
            "moonParentalControlSetting",
            "moonParentalControlSetting:update",
            "moonParentalControlSettingState",
            "moonPairingState",
            "moonSmartDevice:administration",
            "moonDailySummary",
            "moonMonthlySummary",
        ]
    },
    "71b963c1b7b6d119": {
        "redirect_url": "npf71b963c1b7b6d119://auth",
        "scopes": [
            *DEFAULT_SCOPES,
            "user.mii",
        ]
    }
}

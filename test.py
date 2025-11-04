
import os
import logging
import asyncio

from dotenv import load_dotenv
from pynintendoauth import NintendoAuth
from pynintendoauth.exceptions import InvalidSessionTokenException

load_dotenv()

_LOGGER = logging.getLogger(__name__)

async def main():
    """Running function"""
    login = True
    client_id = os.environ.get("CLIENT_ID")
    scopes = os.environ.get("SCOPES")
    if scopes is not None:
        scopes = scopes.split(" ")
    redir_url = os.environ.get("REDIRECT_URL")
    while login:
        try:
            if bool(int(os.environ.get("USE_SESSION_TOKEN", 0))) or input("Should we use a session token? [N/y] ").upper() == "Y":
                auth = NintendoAuth(
                    client_id=client_id,
                    scopes=scopes,
                    redirect_url=redir_url,
                    session_token=os.environ.get("SESSION_TOKEN")
                )
                await auth.async_complete_login(use_session_token=True)
            else:
                auth = NintendoAuth(
                    client_id=client_id,
                    scopes=scopes,
                    redirect_url=redir_url,
                )
                _LOGGER.info("Login using %s", auth.login_url)
                await auth.async_complete_login(input("Response URL: "))
            _LOGGER.info("Logged in, ready.")
            _LOGGER.debug("Access token is: %s", auth.access_token)
            _LOGGER.debug("Session token is: %s", auth.session_token)
            login = False
        except InvalidSessionTokenException as err:
            _LOGGER.error("Invalid session token provided: %s", err)
        except Exception as err:
            _LOGGER.exception(err)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())

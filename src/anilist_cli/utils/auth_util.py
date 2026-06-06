import keyring
from keyring.credentials import Credential


def get_credential() -> Credential | None:
    """
    Helper function which retrieves the Anilist credential if it exists

    @rtype: Credential | None
    @returns: returns object containing Anilist username and access token if it exists
    """
    return keyring.get_credential("Anilist", "")


def set_access_token(username: str, token: str) -> bool:
    """
    Helper function which sets the Anilist access token in credential manager

    @type username: str
    @type token: str
    @param username: Anilist username corresponding to the access token
    @param token: Anilist access token to authorize mutation API requests
    @rtype: bool
    @returns: returns whether or not the saving was successful
    """

    keyring.set_password("Anilist", username, token)

    return True


def delete_access_token() -> bool:
    """
    Helper function which deletes the Anilist access token from the credential manager
    if it exists

    @rtype: bool
    @returns: returns whether or not the deletion of the credential was successful
    """

    credential = get_credential()

    if not credential:
        return False

    keyring.delete_password("Anilist", credential.username)

    return True

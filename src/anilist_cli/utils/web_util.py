import webbrowser


def request_user_auth() -> None:
    """
    Helper function that opens web browser to Anilist authorization URL
    """
    client_id: int = 21872
    authorization_url: str = (
        f"https://anilist.co/api/v2/oauth/authorize?client_id={client_id}&response_type=token"
    )

    webbrowser.open(authorization_url)

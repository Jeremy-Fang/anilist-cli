import keyring

from anilist_cli.utils.auth_util import *


def test_get_credential_exists():
    assert get_credential() != False

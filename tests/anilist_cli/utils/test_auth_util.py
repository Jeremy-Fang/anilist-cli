from unittest.mock import MagicMock, patch

from anilist_cli.utils.auth_util import delete_access_token, get_credential, set_access_token


def test_get_credential_returns_none_when_not_set():
    with patch("keyring.get_credential", return_value=None):
        assert get_credential() is None


def test_get_credential_returns_credential_when_set():
    mock_credential = MagicMock()
    mock_credential.username = "testuser"
    mock_credential.password = "testtoken"
    with patch("keyring.get_credential", return_value=mock_credential):
        result = get_credential()
        assert result is not None
        assert result.username == "testuser"
        assert result.password == "testtoken"


def test_set_access_token_calls_keyring_and_returns_true():
    with patch("keyring.set_password") as mock_set:
        result = set_access_token("testuser", "testtoken")
        assert result is True
        mock_set.assert_called_once_with("Anilist", "testuser", "testtoken")


def test_delete_access_token_returns_false_when_no_credential():
    with patch("keyring.get_credential", return_value=None):
        assert delete_access_token() is False


def test_delete_access_token_deletes_and_returns_true():
    mock_credential = MagicMock()
    mock_credential.username = "testuser"
    with patch("keyring.get_credential", return_value=mock_credential), \
         patch("keyring.delete_password") as mock_delete:
        result = delete_access_token()
        assert result is True
        mock_delete.assert_called_once_with("Anilist", "testuser")

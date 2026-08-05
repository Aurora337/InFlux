from pathlib import Path
from tempfile import TemporaryDirectory

from influx.wallet.manager import WalletManager
from nacl.signing import SigningKey


def test_account_create_and_key_persistence():
    with TemporaryDirectory() as td:
        base = Path(td)
        mgr = WalletManager(base)
        acct = mgr.create_account("acct-x", "id-x", 1)
        assert acct.account_id == "acct-x"

        sk = SigningKey.generate()
        sk_hex = sk.encode().hex()
        pk_hex = sk.verify_key.encode().hex()

        entry = mgr.add_key_for_account("acct-x", sk_hex, pk_hex, created_at=2)
        assert entry.version == 1

        loaded = mgr.load_account("acct-x")
        assert loaded is not None
        assert loaded.key_version == 1

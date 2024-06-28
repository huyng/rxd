import hashlib
import hmac
import typing as t
from cryptography.fernet import Fernet


def verify_hmac_signature(secret: t.Union[str, bytes],
                          payload: t.Union[str, bytes],
                          signature: str):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload: original request body to verify (request.body())
        secret: GitHub app webhook token (WEBHOOK_SECRET)
        signature: header received from GitHub (x-hub-signature-256)
    """
    if not signature:
        return False

    expected_signature = generate_hmac_signature(secret, payload)

    # signature generated from body did not match expected_signature
    if not hmac.compare_digest(expected_signature, signature):
        return False

    return True


def generate_hmac_signature(secret: t.Union[str, bytes],
                            payload: t.Union[str, bytes]):
    """
    Generate a signature given secret and payload
    """
    payload_bytes = payload.encode('utf-8') \
        if isinstance(payload, str) \
        else payload

    secret_bytes = secret.encode('utf-8') \
        if isinstance(secret, str) \
        else secret

    hash = hmac.new(secret_bytes,
                    msg=payload_bytes,
                    digestmod=hashlib.sha256)
    return "sha256=" + hash.hexdigest()


class Cipher:

    def __init__(self, key=None):
        self.key = key

    def generate_key(self) -> bytes:
        self.key = Fernet.generate_key()
        return self.key

    def encrypt(self, message: str) -> bytes:
        if self.key is None:
            raise Exception("Key has not been set")

        f = Fernet(self.key)
        return f.encrypt(message.encode('utf-8'))

    def decrypt(self, encrypted_message: bytes) -> str:
        if self.key is None:
            raise Exception("Key has not been set")

        f = Fernet(self.key)
        return f.decrypt(encrypted_message).decode('utf-8')


def test_hmac_verification():
    secret = "hello world"
    payload = "This is a test payload"
    signature = generate_hmac_signature(secret, payload)
    is_verified = verify_hmac_signature(secret, payload, signature)
    assert is_verified, "generated signature does not match expected signature"


def test_Cipher():
    message = "This is a test payload"
    cipher = Cipher()
    cipher.generate_key()
    encrypted_message = cipher.encrypt(message)
    decrypted_message = cipher.decrypt(encrypted_message)
    assert message == decrypted_message

    # generate a new key and make sure we can not decrypt
    cipher.generate_key()
    decrypted_message = cipher.decrypt(encrypted_message)
    assert message == decrypted_message

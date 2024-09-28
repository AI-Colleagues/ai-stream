"""Init script for utils."""

import base64
import uuid


def create_id() -> str:
    """Create a random string ID."""
    uuid_bytes = uuid.uuid4().bytes
    return base64.urlsafe_b64encode(uuid_bytes).rstrip(b"=").decode("ascii")

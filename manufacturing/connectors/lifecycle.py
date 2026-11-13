"""The connector lifecycle every LEGION manufacturing connector follows (WO-LMFG-001, Phase B):

    DISCONNECTED -> CONFIGURED -> AUTHENTICATED -> SCOPED -> VERIFIED

Any failure or expiry moves the connector to UNAVAILABLE, from which only a fresh configure() restarts it.
A connector grants no execution authority: it reads. Authentication success is never treated as permission to act,
and a configuration file alone never moves the state past CONFIGURED (INV-03: config is not connectivity).
"""
from __future__ import annotations

import time

ORDER = ["DISCONNECTED", "CONFIGURED", "AUTHENTICATED", "SCOPED", "VERIFIED"]
UNAVAILABLE = "UNAVAILABLE"


class LifecycleError(RuntimeError):
    pass


class NotVerified(LifecycleError):
    """A read was attempted on a connector that is not VERIFIED."""


class WriteRefused(LifecycleError):
    """A write, or any call outside the documented read set, was attempted."""


class Lifecycle:
    def __init__(self, system: str, clock=time.time):
        self.system, self.state, self.clock = system, "DISCONNECTED", clock
        self.history = [("DISCONNECTED", None)]
        self.expires_at = None
        self.tenant = None
        self.scopes = ()

    def _to(self, state, why=None):
        self.state = state
        self.history.append((state, why))

    def _advance(self, expected_from, to):
        self.check_expiry()
        if self.state != expected_from:
            raise LifecycleError(f"{self.system}: {to} requires {expected_from}, state is {self.state}")
        self._to(to)

    def configure(self, config: dict):
        if self.state not in ("DISCONNECTED", UNAVAILABLE):
            raise LifecycleError(f"{self.system}: configure from {self.state}")
        self.state = "DISCONNECTED"
        if not config:
            return self.fail("EMPTY_CONFIGURATION")
        self._to("CONFIGURED")

    def authenticated(self, tenant: str, expires_at: float | None):
        if not tenant:
            return self.fail("AUTHENTICATION_RETURNED_NO_TENANT")
        self._advance("CONFIGURED", "AUTHENTICATED")
        self.tenant, self.expires_at = tenant, expires_at

    def scoped(self, scopes):
        scopes = tuple(sorted(set(scopes or ())))
        if not scopes:
            return self.fail("NO_PERMITTED_SCOPE")
        self._advance("AUTHENTICATED", "SCOPED")
        self.scopes = scopes

    def verified(self, readback_ok: bool, detail: str = ""):
        if not readback_ok:
            return self.fail("READBACK_FAILED " + detail)
        self._advance("SCOPED", "VERIFIED")

    def fail(self, why: str):
        self._to(UNAVAILABLE, why)
        self.tenant, self.scopes, self.expires_at = None, (), None
        return self.state

    def check_expiry(self):
        if self.expires_at is not None and self.clock() >= self.expires_at:
            self.fail("CREDENTIAL_EXPIRED")

    def require_verified(self):
        self.check_expiry()
        if self.state != "VERIFIED":
            raise NotVerified(f"{self.system} is {self.state}: no read is made and no data is returned")

    @property
    def grants_execution_authority(self) -> bool:
        return False   # by construction, for every state

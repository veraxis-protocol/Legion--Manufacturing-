"""WO-B02: Microsoft 365, read-only, through Microsoft Graph (the Microsoft-supported API).

What the upstream skills read from M365 (onboarding, customer-inquiry-intake, data-consolidate,
supplier-quote-request): Outlook RFQ mail and its attachments, SharePoint/OneDrive files, and the Excel exports in the
plant's export folder. The adapter reads those and nothing else:
  - GET only, on an allow-list of Graph paths; every other method or path is refused before the transport is touched
  - source identity is kept: message id and internetMessageId, attachment id, driveItem id, eTag and cTag (revision)
  - 403 is "access denied" and is reported as such, never as an empty folder
  - 401 moves the connector to UNAVAILABLE (expired or revoked credential)
  - no browser scraping and no fabricated inbox data: the transport is Graph or a recorded Graph response
"""
from __future__ import annotations

import re

from manufacturing.connectors.common import Adapter
from manufacturing.connectors.lifecycle import LifecycleError

GRAPH = "https://graph.microsoft.com/v1.0"
READ_PATHS = [
    r"/me",
    r"/organization",
    r"/(me|users/[^/]+)/messages(\?.*)?",
    r"/(me|users/[^/]+)/messages/[^/?]+(\?.*)?",
    r"/(me|users/[^/]+)/messages/[^/]+/attachments(\?.*)?",
    r"/(me|users/[^/]+)/messages/[^/]+/attachments/[^/?]+(/\$value)?",
    r"/sites/[^/]+/drives/[^/]+/(root|items/[^/]+)(/children)?(\?.*)?",
    r"/sites/[^/]+/drives/[^/]+/items/[^/]+/(content|versions)",
    r"/(me|sites/[^/]+)/drive/items/[^/]+(/(content|children|versions))?",
    r"/sites/[^/]+/drives/[^/]+/items/[^/]+/workbook/worksheets(/[^/]+/usedRange)?(\?.*)?",
]
READ_SCOPES = {"Mail.Read", "Files.Read.All", "Sites.Read.All", "User.Read"}
WRITE_SCOPE = re.compile(r"\.(ReadWrite|Write|Send|Manage)", re.I)


class M365(Adapter):
    system = "m365"
    source_system = "m365"

    def connect(self, config: dict):
        self.lc.configure(config)
        if self.lc.state != "CONFIGURED":
            return self.lc.state
        org = self.request("GET", "/organization")
        if org.get("status") == 401:
            return self.lc.fail("UNAUTHENTICATED_OR_EXPIRED")
        tid = (org.get("value") or [{}])[0].get("id")
        if config.get("tenant_id") and tid != config["tenant_id"]:
            return self.lc.fail(f"TENANT_MISMATCH connected={tid} configured={config['tenant_id']}")
        self.lc.authenticated(tid or "", config.get("expires_at"))
        if self.lc.state != "AUTHENTICATED":
            return self.lc.state
        granted = set(config.get("granted_scopes") or [])
        usable = sorted(granted & READ_SCOPES)
        self.ignored_write_scopes = sorted(s for s in granted if WRITE_SCOPE.search(s))
        if not usable:
            return self.lc.fail("NO_READ_SCOPE_GRANTED")
        self.lc.scoped(usable)
        self.lc.verified(True)
        return self.lc.state

    def request(self, method: str, path: str, params=None):
        if method != "GET" or not any(re.fullmatch(p, path) for p in READ_PATHS):
            self.refuse_write(f"{method} {path}", params)
        self.log.add("read", f"{method} {path}", params)
        return self.transport(method, GRAPH + path, dict(params or {}))

    def _get(self, path, params=None):
        self.lc.require_verified()
        res = self.request("GET", path, params)
        st = res.get("status", 200)
        if st == 401:
            self.lc.fail("CREDENTIAL_EXPIRED")
            raise LifecycleError("credential expired during a read; connector is UNAVAILABLE")
        if st == 403:
            return {"denied": True, "path": path, "detail": res.get("error")}
        if st == 404:
            return {"not_found": True, "path": path}
        if res.get("tenant") not in (None, self.lc.tenant):
            raise LifecycleError("response from another tenant; refused")
        return res

    def rfq_messages(self, mailbox: str, query: str) -> list:
        res = self._get(f"/{mailbox}/messages", {"$search": query})
        if res.get("denied"):
            return [{"denied": True, "detail": res.get("detail")}]
        out = []
        for m in res.get("value") or []:
            out.append({"source_ref": f"m365:message/{m['id']}", "message_id": m["id"],
                        "internet_message_id": m.get("internetMessageId"), "subject": m.get("subject"),
                        "from": (m.get("from") or {}).get("emailAddress", {}).get("address"),
                        "received_at": m.get("receivedDateTime"), "has_attachments": m.get("hasAttachments"),
                        "body_preview": m.get("bodyPreview")})
        return out

    def attachments(self, mailbox: str, message_id: str) -> list:
        res = self._get(f"/{mailbox}/messages/{message_id}/attachments")
        if res.get("denied"):
            return [{"denied": True}]
        return [{"source_ref": f"m365:message/{message_id}/attachment/{a['id']}", "attachment_id": a["id"],
                 "name": a.get("name"), "content_type": a.get("contentType"), "size": a.get("size"),
                 "last_modified": a.get("lastModifiedDateTime")} for a in res.get("value") or []]

    def drive_item(self, site: str, drive: str, item: str) -> dict:
        res = self._get(f"/sites/{site}/drives/{drive}/items/{item}")
        if res.get("denied") or res.get("not_found"):
            return res
        return {"source_ref": f"m365:driveItem/{res['id']}", "item_id": res["id"], "name": res.get("name"),
                "etag": res.get("eTag"), "ctag": res.get("cTag"),
                "last_modified": res.get("lastModifiedDateTime"), "web_url": res.get("webUrl"),
                "revision": res.get("cTag") or res.get("eTag")}

    def worksheet_rows(self, site: str, drive: str, item: str, sheet: str) -> dict:
        meta = self.drive_item(site, drive, item)
        if meta.get("denied") or meta.get("not_found"):
            return meta
        res = self._get(f"/sites/{site}/drives/{drive}/items/{item}/workbook/worksheets/{sheet}/usedRange")
        if res.get("denied"):
            return res
        values = res.get("values") or []
        if not values:
            return {"source": meta, "header": None, "rows": [], "empty_sheet": True}
        header, body = values[0], values[1:]
        return {"source": meta, "header": header,
                "rows": [{"source_ref": f"{meta['source_ref']}#{sheet}!row{i + 2}", **dict(zip(header, r))}
                         for i, r in enumerate(body)]}

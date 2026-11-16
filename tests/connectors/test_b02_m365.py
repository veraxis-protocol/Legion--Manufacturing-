"""WO-B02 contract suite: Microsoft 365 adapter over Microsoft Graph, on scripted Graph-shaped responses
(fakes.py, SYNTHETIC). Live acceptance B02-T01..T08 stays BLOCKED until an authorized tenant is configured."""
import unittest

from manufacturing.connectors.lifecycle import LifecycleError, NotVerified, WriteRefused
from manufacturing.connectors.m365 import M365
from tests.connectors.fakes import GraphFake

TENANT = "00000000-0000-0000-0000-00000000c0de"
MSG = {"id": "AAMkAD-rfq-1", "internetMessageId": "<rfq-0912@example.test>", "subject": "RFQ EH-RFQ-0912",
       "from": {"emailAddress": {"address": "buyer@example.test"}}, "receivedDateTime": "2026-10-12T14:02:00Z",
       "hasAttachments": True, "bodyPreview": "Please quote 500 pcs PN-4471-B rev 2"}
ROUTES = {
    "/me/messages": {"status": 200, "value": [MSG]},
    "/me/messages/AAMkAD-rfq-1/attachments": {"status": 200, "value": [
        {"id": "att-1", "name": "4471-B_rev2.pdf", "contentType": "application/pdf", "size": 182044,
         "lastModifiedDateTime": "2026-10-12T14:01:00Z"}]},
    "/sites/plant/drives/exports/items/x1": {"status": 200, "id": "x1", "name": "prod-output-20261012.xlsx",
                                             "eTag": "\"{ABC},4\"", "cTag": "\"c:{ABC},7\"",
                                             "lastModifiedDateTime": "2026-10-13T02:00:00Z"},
    "/sites/plant/drives/exports/items/x1/workbook/worksheets/Sheet1/usedRange": {
        "status": 200, "values": [["production_wo", "part", "qty_good", "qty_scrap"], ["WO-88201", "PN-4471-B", 486, 14]]},
    "/sites/plant/drives/exports/items/secret": {"status": 403, "error": {"code": "accessDenied"}},
}


def connected(routes=ROUTES, cfg=None):
    a = M365(GraphFake(TENANT, dict(routes)), {})
    a.connect(cfg or {"tenant_id": TENANT, "granted_scopes": ["Mail.Read", "Files.Read.All", "Sites.Read.All"]})
    return a


class M365Contract(unittest.TestCase):
    def test_t01_permitted_scopes_only(self):
        a = connected(cfg={"tenant_id": TENANT, "granted_scopes": ["Mail.Read", "Mail.ReadWrite", "Files.ReadWrite.All"]})
        self.assertEqual(a.lc.state, "VERIFIED")
        self.assertEqual(a.lc.scopes, ("Mail.Read",))
        self.assertEqual(a.ignored_write_scopes, ["Files.ReadWrite.All", "Mail.ReadWrite"])
        b = connected(cfg={"tenant_id": TENANT, "granted_scopes": ["Mail.Send"]})
        self.assertEqual(b.lc.state, "UNAVAILABLE")

    def test_t02_t03_rfq_and_attachments_keep_identity(self):
        a = connected()
        m = a.rfq_messages("me", "RFQ")[0]
        self.assertEqual((m["message_id"], m["internet_message_id"]), ("AAMkAD-rfq-1", "<rfq-0912@example.test>"))
        att = a.attachments("me", m["message_id"])[0]
        self.assertEqual(att["source_ref"], "m365:message/AAMkAD-rfq-1/attachment/att-1")

    def test_t04_t05_export_rows_carry_file_revision_and_row(self):
        res = connected().worksheet_rows("plant", "exports", "x1", "Sheet1")
        self.assertEqual(res["source"]["revision"], "\"c:{ABC},7\"")
        self.assertEqual(res["rows"][0]["source_ref"], "m365:driveItem/x1#Sheet1!row2")
        self.assertEqual(res["rows"][0]["qty_good"], 486)

    def test_t06_denied_is_denied_not_empty(self):
        res = connected().drive_item("plant", "exports", "secret")
        self.assertTrue(res["denied"])
        self.assertNotIn("rows", res)

    def test_t07_expired_credentials(self):
        a = connected(routes={**ROUTES, "/organization": {"status": 401}})
        self.assertEqual(a.lc.state, "UNAVAILABLE")
        with self.assertRaises(NotVerified):
            a.rfq_messages("me", "RFQ")
        t = {"now": 0}
        b = M365(GraphFake(TENANT, dict(ROUTES)), {}, clock=lambda: t["now"])
        b.connect({"tenant_id": TENANT, "granted_scopes": ["Mail.Read"], "expires_at": 10})
        t["now"] = 11
        with self.assertRaises(NotVerified):
            b.rfq_messages("me", "RFQ")

    def test_t08_zero_writes(self):
        a = connected()
        n = len(a.transport.calls)
        for m, p in (("POST", "/me/sendMail"), ("POST", "/me/messages/AAMkAD-rfq-1/reply"),
                     ("PATCH", "/me/messages/AAMkAD-rfq-1"), ("PUT", "/sites/plant/drives/exports/items/x1/content"),
                     ("DELETE", "/me/messages/AAMkAD-rfq-1"), ("GET", "/me/mailFolders/inbox/messageRules")):
            with self.assertRaises(WriteRefused):
                a.request(m, p)
        self.assertEqual(len(a.transport.calls), n)
        self.assertEqual(a.log.writes, [])

    def test_wrong_tenant_refused(self):
        a = connected(cfg={"tenant_id": "11111111-1111-1111-1111-111111111111", "granted_scopes": ["Mail.Read"]})
        self.assertEqual(a.lc.state, "UNAVAILABLE")

    def test_response_from_another_tenant_refused(self):
        routes = {**ROUTES, "/me/messages": {"status": 200, "tenant": "evil", "value": [MSG]}}
        with self.assertRaises(LifecycleError):
            connected(routes).rfq_messages("me", "RFQ")


if __name__ == "__main__":
    unittest.main()

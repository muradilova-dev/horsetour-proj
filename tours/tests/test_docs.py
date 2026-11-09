from .base import BaseTest


class DocsTest(BaseTest):
    def test_schema_available(self):
        r = self.client.get("/api/schema/")
        self.assertEqual(r.status_code, 200)

    def test_swagger_and_redoc_pages(self):
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)
        self.assertEqual(self.client.get("/api/redoc/").status_code, 200)

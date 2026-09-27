import unittest
from backend.app import create_app
from backend.app.database import db

class DocsOpenAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_openapi_json_schema(self):
        """GET /api/openapi.json returns valid OpenAPI 3.0 specification"""
        resp = self.client.get('/api/openapi.json')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['openapi'], '3.0.3')
        self.assertIn('info', data)
        self.assertIn('paths', data)
        self.assertIn('/api/emergency/trigger', data['paths'])
        self.assertIn('/api/location/update', data['paths'])
        self.assertIn('/api/routes/calculate', data['paths'])

    def test_swagger_ui_html_render(self):
        """GET /api/docs and /docs return Swagger UI bundle HTML"""
        for url in ['/api/docs', '/docs']:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('SafeRoute Saheli API Reference', html)
            self.assertIn('swagger-ui-bundle.js', html)
            self.assertIn('/api/openapi.json', html)

if __name__ == '__main__':
    unittest.main()

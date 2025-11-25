from starlette.testclient import TestClient

from app.main import app


class TestUserAPI:
    def setup_method(self):
        self.client = TestClient(app)
        self.base_url = "/api/v1/search"

    def test_full_user_crud_flow(self):
        # POST
        user_data = \
            {
                "query": "Math",
                "filters": {
                    "authors": None,
                    "journal_title": None,
                    "article_title": None,
                    "year_from": None,
                    "year_to": None,
                    "article_text": None,
                    "abstract": None,
                    "affiliation": None,
                    "authors_count": None,
                    "collaboration_countries": None
                }
        }
        create_response = self.client.post(f"{self.base_url}/", json=user_data)
        assert create_response.status_code == 200
        request = create_response.json()
        return request

test = TestUserAPI()
test.setup_method()
print(test.test_full_user_crud_flow())
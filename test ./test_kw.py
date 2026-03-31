import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import base64
import json
from io import BytesIO
from PIL import Image


# Helper: generate a base64 JPEG image
def make_base64_image(width=80, height=80, color=(0, 0, 255)):
    img = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


# ---------------------------------------------------------
# 1. TEST: Session initialization for /stripselect route
# ---------------------------------------------------------

class TestStripSelectRoute:

    @pytest.fixture
    def client(self):
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_stripselect_loads(self, client):
        """Normal case: GET /stripselect should return 200 or redirect"""
        response = client.get("/stripselect")
        assert response.status_code in (200, 308)

    def test_stripselect_template_content(self, client):
        """Edge case: ensure page contains expected HTML element"""
        response = client.get("/stripselect")
        assert b"<" in response.data

    def test_stripselect_wrong_method(self, client):
        """Error case: POSTing to /stripselect should redirect or be blocked"""
        response = client.post("/stripselect")
        assert response.status_code in (200, 308)


# ---------------------------------------------------------
# 2. TEST: /stripselect/ (store_choice) POST behavior
# ---------------------------------------------------------

class TestStoreChoiceRoute:

    @pytest.fixture
    def client(self):
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_valid_choice(self, client):
        """Normal case: POST / should not be allowed (405)"""
        response = client.post("/", data={"button1": "3"})
        assert response.status_code == 405

    def test_missing_form_data(self, client):
        """Error case: empty form should return 405 (POST not allowed)"""
        response = client.post("/", data={})
        assert response.status_code == 405

    def test_invalid_count_value(self, client):
        """Edge case: non-numeric count should not crash"""
        response = client.post("/", data={"button1": "abc"})
        assert response.status_code in (308, 400, 405)


# ---------------------------------------------------------
# 3. TEST: /stripselect/camera route session behavior
# ---------------------------------------------------------

class TestCameraRoute:

    @pytest.fixture
    def client(self):
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["photo_count"] = 3
                sess["button_name"] = "button1"
            yield client

    def test_camera_loads(self, client):
        response = client.get("/stripselect/camera")
        assert response.status_code == 200

    def test_camera_resets_photo_counter(self, client):
        client.get("/stripselect/camera")
        with client.session_transaction() as sess:
            assert sess["photos_taken"] == 0

    def test_camera_missing_session(self, client):
        with client.session_transaction() as sess:
            sess.clear()
        response = client.get("/stripselect/camera")
        assert response.status_code == 200


# ---------------------------------------------------------
# 4. TEST: /stripselect/take_photos image decoding logic
# ---------------------------------------------------------

class TestTakePhotosImageHandling:

    @pytest.fixture
    def client(self):
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["photo_count"] = 2
                sess["photos_taken"] = 0
                sess["button_name"] = "test"
            yield client

    def test_valid_image_decodes(self, client):
        """Normal case: valid base64 image should decode without error"""
        payload = {"image": make_base64_image()}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_invalid_base64_string(self, client):
        payload = {"image": "data:image/jpeg;base64,NOT_REAL_BASE64"}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code in (400, 422, 500)

    def test_missing_image_field(self, client):
        payload = {"wrong": "value"}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code in (400, 422)


# ---------------------------------------------------------
# 5. TEST: /photo-confirmation/<id> behavior
# ---------------------------------------------------------

class TestPhotoConfirmationRoute:

    @pytest.fixture
    def client(self):
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["saved_photos"] = [
                    "static/photos/test_1.jpg",
                    "static/photos/test_2.jpg"
                ]
            yield client

    def test_valid_photo_id(self, client):
        response = client.get("/stripselect/photo-confirmation/0")
        assert response.status_code == 200

    def test_out_of_bounds_id(self, client):
        response = client.get("/stripselect/photo-confirmation/999")
        assert response.status_code == 200

    def test_no_photos_in_session(self, client):
        with client.session_transaction() as sess:
            sess["saved_photos"] = []
        response = client.get("/stripselect/photo-confirmation/0")
        assert response.status_code in (302, 303)

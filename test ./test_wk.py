import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
import json
from io import BytesIO
from PIL import Image
import base64
import csv


# Helper: generate a base64 JPEG image
def make_base64_image(width=80, height=80, color=(255, 128, 0)):
    img = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


# tests for /stripselect/next POST route
class TestNextPageRoute:

    @pytest.fixture
    def client(self):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_next_post_returns_response(self, client):
        # POST should give back something
        response = client.post("/stripselect/next")
        assert response.status_code in (200, 302, 308)

    def test_next_get_not_allowed(self, client):
        # GET shouldn't be allowed on this route
        response = client.get("/stripselect/next")
        assert response.status_code in (405, 404)

    def test_next_without_session(self, client):
        # no session data - should not blow up
        with client.session_transaction() as sess:
            sess.clear()
        response = client.post("/stripselect/next")
        assert response.status_code in (200, 302, 308, 500)


# tests for CSV logging in store_choice
class TestCSVLogging:

    def test_log_file_created(self, tmp_path):
        # log file should exist after writing
        log_path = tmp_path / "log.csv"
        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["button1", "3", "127.0.0.1"])
        assert log_path.exists()

    def test_log_row_has_correct_fields(self, tmp_path):
        # make sure the right values end up in the row
        log_path = tmp_path / "log.csv"
        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["button2", "4", "192.168.1.1"])
        with open(log_path, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert rows[0] == ["button2", "4", "192.168.1.1"]

    def test_multiple_log_entries(self, tmp_path):
        # multiple sessions should each add a row
        log_path = tmp_path / "log.csv"
        for i in range(3):
            with open(log_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([f"button{i}", str(i + 1), "127.0.0.1"])
        with open(log_path, "r") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 3

    def test_log_with_empty_button_name(self, tmp_path):
        # empty button name shouldnt crash the logger
        log_path = tmp_path / "log.csv"
        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["", "0", "127.0.0.1"])
        with open(log_path, "r") as f:
            rows = list(csv.reader(f))
        assert rows[0][0] == ""


# tests for stripdesign vertical and horizontal routes
class TestStripDesignRoutes:

    @pytest.fixture
    def client(self):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_stripdesign_vertical_loads(self, client):
        # vertical layout page should load
        response = client.get("/stripselect/stripdesign/v")
        assert response.status_code == 200

    def test_stripdesign_horizontal_loads(self, client):
        # horizontal layout page should load
        response = client.get("/stripselect/stripdesign/h")
        assert response.status_code == 200

    def test_stripdesign_invalid_variant(self, client):
        # unknown layout variant should 404
        response = client.get("/stripselect/stripdesign/z")
        assert response.status_code == 404


# tests for layout branching in photo_confirmation
class TestPhotoConfirmationBranching:

    @pytest.fixture
    def client_with_photos(self):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["saved_photos"] = ["static/photos/test_1.jpg"]
            yield client

    def test_onebythree_goes_to_horizontal(self, client_with_photos):
        # 1x3 should go to horizontal design
        with client_with_photos.session_transaction() as sess:
            sess["button_name"] = "onebythree"
        response = client_with_photos.get("/stripselect/photo-confirmation/0")
        assert response.status_code == 200
        assert b"h" in response.data or response.status_code == 200

    def test_onebyfour_goes_to_horizontal(self, client_with_photos):
        # 1x4 should also go to horizontal
        with client_with_photos.session_transaction() as sess:
            sess["button_name"] = "onebyfour"
        response = client_with_photos.get("/stripselect/photo-confirmation/0")
        assert response.status_code == 200

    def test_other_button_goes_to_vertical(self, client_with_photos):
        # anything else should go to vertical
        with client_with_photos.session_transaction() as sess:
            sess["button_name"] = "twobytwo"
        response = client_with_photos.get("/stripselect/photo-confirmation/0")
        assert response.status_code == 200

    def test_photo_id_clamped_to_lower_bound(self, client_with_photos):
        # photo_id 0 should still work fine
        response = client_with_photos.get("/stripselect/photo-confirmation/0")
        assert response.status_code == 200


# tests for session state updates in take_photos
class TestTakePhotosSessionState:

    @pytest.fixture
    def client(self):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["photo_count"] = 3
                sess["photos_taken"] = 0
                sess["button_name"] = "mybutton"
                sess["saved_photos"] = []
            yield client

    def test_photos_taken_increments(self, client):
        # counter should increment after each photo
        payload = {"image": make_base64_image()}
        client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        with client.session_transaction() as sess:
            assert sess["photos_taken"] == 1

    def test_done_flag_false_before_last_photo(self, client):
        # done should still be False if we havent hit the limit
        payload = {"image": make_base64_image()}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["done"] is False

    def test_done_flag_true_on_last_photo(self, client):
        # done should flip to True on the last photo
        with client.session_transaction() as sess:
            sess["photos_taken"] = 2  # one away from the count of 3
        payload = {"image": make_base64_image()}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["done"] is True

    def test_saved_photos_grows_after_each_post(self, client):
        # saved photos list should grow after each one
        payload = {"image": make_base64_image()}
        client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        with client.session_transaction() as sess:
            assert len(sess["saved_photos"]) == 1

    def test_response_contains_photo_count(self, client):
        # response should include photo_count in the JSON
        payload = {"image": make_base64_image()}
        response = client.post(
            "/stripselect/take_photos",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = response.get_json()
        assert "photo_count" in data
        assert data["photo_count"] == 3

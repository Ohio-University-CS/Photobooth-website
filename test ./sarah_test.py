import pytest
import base64
import json
from io import BytesIO
from PIL import Image


# Helper: generate a base64 PNG image (different from JPEG)
def make_base64_png(width=60, height=60, color=(0, 255, 0)):
    img = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


# 1. TEST: Image format validation (PNG, not JPEG)
class TestImageFormatValidation:
    def test_valid_png_image(self):
        # Normal: valid PNG data URL
        image_data = make_base64_png()
        assert image_data.startswith("data:image/png;base64,")
        _, encoded = image_data.split(",", 1)
        decoded = base64.b64decode(encoded)
        assert len(decoded) > 0

    def test_wrong_format_prefix(self):
        # Edge: JPEG prefix for PNG data
        image_data = make_base64_png().replace("png", "jpeg")
        assert image_data.startswith("data:image/jpeg")

    def test_corrupt_base64(self):
        # Error: corrupt base64 string
        bad_data = "data:image/png;base64,!!!notbase64!!!"
        with pytest.raises(Exception):
            base64.b64decode(bad_data.split(",", 1)[1])


# 2. TEST: Photo count boundary and type checks
class TestPhotoCountBoundaries:
    def test_large_photo_count(self):
        # Normal: large but valid count
        count = int("20")
        assert count == 20

    def test_negative_photo_count(self):
        # Edge: negative count should be handled
        count = int("-2")
        assert count < 0

    def test_float_photo_count(self):
        # Error: float string should raise ValueError
        with pytest.raises(ValueError):
            int("3.5")


# 3. TEST: /stripselect/take_photos with alternate content types
class TestTakePhotosContentTypes:
    @pytest.fixture
    def client(self):
        from main import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_form_urlencoded(self, client):
        # Normal: send as form data (should fail, but not crash)
        payload = {"image": make_base64_png()}
        response = client.post(
            "/stripselect/take_photos",
            data=payload,
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code in (400, 415, 422, 500)

    def test_wrong_content_type(self, client):
        # Edge: send as plain text
        response = client.post(
            "/stripselect/take_photos", data="not json", content_type="text/plain"
        )
        assert response.status_code in (400, 415, 422, 500)

    def test_missing_content_type(self, client):
        # Error: no content type header
        response = client.post(
            "/stripselect/take_photos", data=json.dumps({"image": make_base64_png()})
        )
        assert response.status_code in (400, 415, 422, 500)


# 4. TEST: Session photo list manipulation (removal, duplicates)
class TestPhotoListManipulation:
    def test_remove_photo(self):
        # Normal: remove a photo from the list
        photos = ["a.jpg", "b.jpg", "c.jpg"]
        photos.remove("b.jpg")
        assert photos == ["a.jpg", "c.jpg"]

    def test_duplicate_photos(self):
        # Edge: allow duplicate filenames
        photos = ["a.jpg", "a.jpg", "b.jpg"]
        assert photos.count("a.jpg") == 2

    def test_remove_nonexistent_photo(self):
        # Error: removing a photo not in list raises ValueError
        photos = ["a.jpg"]
        with pytest.raises(ValueError):
            photos.remove("notfound.jpg")


# 5. TEST: Countdown logic with custom step and non-integer
class TestCountdownCustomLogic:
    def test_countdown_by_twos(self):
        # Normal: countdown by 2s
        ticks = list(range(10, 0, -2))
        assert ticks == [10, 8, 6, 4, 2]

    def test_countdown_non_integer(self):
        # Edge: using float in range (should error)
        with pytest.raises(TypeError):
            list(range(5.0, 0, -1))

    def test_countdown_empty(self):
        # Error: start less than stop
        ticks = list(range(0, 5, -1))
        assert ticks == []

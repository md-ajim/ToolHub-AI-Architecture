import io
from unittest.mock import patch
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient
from apps.image_tools.services import (
    resize_image,
    compress_image,
    convert_image,
    crop_image,
    rotate_image,
    watermark_image,
    flip_image,
    product_image,
    mockup_generator,
)
from apps.image_tools.models import ImageProcessingJob
from apps.image_tools.tasks import process_image_job


class ImageToolServicesTest(SimpleTestCase):
    def _make_image(self, mode="RGB", size=(200, 200)):
        img = Image.new(mode, size, color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    def _make_file(self, buf, name="test.png"):
        from django.core.files.uploadedfile import InMemoryUploadedFile
        return InMemoryUploadedFile(buf, "ImageField", name, "image/png", buf.tell(), None)

    def test_resize_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = resize_image(f, 100, 100)
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (100, 100))

    def test_crop_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = crop_image(f, 50, 50, 100, 100)
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (100, 100))

    def test_rotate_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = rotate_image(f, 90)
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertGreater(img.size[0], 0)

    def test_flip_image_horizontal(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = flip_image(f, "horizontal")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (200, 200))

    def test_flip_image_vertical(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = flip_image(f, "vertical")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (200, 200))

    def test_convert_image_to_jpeg(self):
        buf = self._make_image()
        f = self._make_file(buf, "test.png")
        result = convert_image(f, "JPEG")
        self.assertIsNotNone(result)
        self.assertIn("jpeg", result.name.lower())

    def test_compress_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = compress_image(f, quality=50)
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (200, 200))

    def test_watermark_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = watermark_image(f, "ToolHub AI")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertGreater(img.size[0], 0)

    def test_product_image(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = product_image(f, style="white")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (200, 200))

    def test_mockup_generator(self):
        buf = self._make_image()
        f = self._make_file(buf)
        result = mockup_generator(f, template="device")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.size, (600, 500))

    def test_resize_preserves_format(self):
        buf = self._make_image()
        f = self._make_file(buf, "test.png")
        result = resize_image(f, 100, 100)
        self.assertIn("png", result.name.lower())

    def test_convert_rgba_to_jpeg(self):
        buf = self._make_image(mode="RGBA", size=(100, 100))
        f = self._make_file(buf, "test.png")
        result = convert_image(f, "JPEG")
        self.assertIsNotNone(result)
        img = Image.open(result)
        self.assertEqual(img.mode, "RGB")


class ImageJobApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _upload(self, name="input.png"):
        buffer = io.BytesIO()
        Image.new("RGB", (20, 20), (120, 80, 40)).save(buffer, format="PNG")
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    @patch("apps.image_tools.views.process_image_job.delay")
    def test_anonymous_job_can_be_polled_and_cancelled(self, delay):
        response = self.client.post(
            "/api/v1/image/resize/",
            {"image": self._upload(), "width": 100, "height": 100},
            format="multipart",
        )
        self.assertEqual(response.status_code, 202, response.content)
        job_id = response.json()["data"]["job_id"]
        delay.assert_called_once()

        status = self.client.get(f"/api/v1/image/job/{job_id}/")
        self.assertEqual(status.status_code, 200)
        self.assertIn(status.json()["data"]["status"], {"queued", "processing"})

        cancelled = self.client.post(f"/api/v1/image/job/{job_id}/cancel/")
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["data"]["status"], ImageProcessingJob.Status.CANCELLED)

    @patch("apps.image_tools.tasks.resize_image")
    def test_cancelled_job_is_not_processed(self, resize_image):
        job = ImageProcessingJob.objects.create(
            user=None,
            tool_name="resize",
            parameters={"width": 100, "height": 100},
            input_file=self._upload(),
            status=ImageProcessingJob.Status.CANCELLED,
        )

        process_image_job.run(job.id)

        resize_image.assert_not_called()
        job.refresh_from_db()
        self.assertEqual(job.status, ImageProcessingJob.Status.CANCELLED)

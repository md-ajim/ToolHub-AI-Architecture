import io
import tempfile

from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from pypdf import PdfWriter
from rest_framework import status
from rest_framework.test import APISimpleTestCase


def make_jpeg(name="image.jpg"):
    output = io.BytesIO()
    Image.new("RGB", (16, 16), "blue").save(output, format="JPEG")
    return SimpleUploadedFile(name, output.getvalue(), content_type="image/jpeg")


def make_pdf(name="document.pdf"):
    output = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(output)
    return SimpleUploadedFile(name, output.getvalue(), content_type="application/pdf")


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class PdfConversionApiTests(APISimpleTestCase):
    def setUp(self):
        super().setUp()
        self.media_root = self.enterContext(tempfile.TemporaryDirectory())
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def test_pdf_to_jpg_returns_downloadable_archive(self):
        response = self.client.post(
            "/api/v1/pdf/to-image/", {"file": make_pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["filename"].endswith(".zip"))

    def test_jpgs_to_pdf_returns_downloadable_pdf(self):
        response = self.client.post(
            "/api/v1/pdf/from-image/", {"images": [make_jpeg()]}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["filename"].endswith(".pdf"))

    def test_pdf_to_jpg_rejects_invalid_pdf(self):
        invalid = SimpleUploadedFile("invalid.pdf", b"not a PDF", content_type="application/pdf")
        response = self.client.post(
            "/api/v1/pdf/to-image/", {"file": invalid}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(response.data["success"])

import io
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image
from pypdf import PdfReader, PdfWriter

from apps.pdf_tools.conversion_services import convert_jpgs_to_pdf, convert_pdf_to_jpg_archive


def make_jpeg(name="image.jpg"):
    output = io.BytesIO()
    Image.new("RGB", (16, 16), "red").save(output, format="JPEG")
    return SimpleUploadedFile(name, output.getvalue(), content_type="image/jpeg")


def make_pdf():
    output = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    writer.write(output)
    return SimpleUploadedFile("document.pdf", output.getvalue(), content_type="application/pdf")


class PdfConversionServiceTests(SimpleTestCase):
    def test_convert_jpgs_to_pdf_preserves_all_images(self):
        result = convert_jpgs_to_pdf([make_jpeg("one.jpg"), make_jpeg("two.jpg")])

        self.assertEqual(result.content_type, "application/pdf")
        self.assertEqual(len(PdfReader(result).pages), 2)

    def test_convert_pdf_to_jpg_returns_zip_archive(self):
        result = convert_pdf_to_jpg_archive(make_pdf())

        self.assertEqual(result.content_type, "application/zip")
        with zipfile.ZipFile(result) as archive:
            self.assertEqual(archive.namelist(), ["page-1.jpg", "page-2.jpg"])

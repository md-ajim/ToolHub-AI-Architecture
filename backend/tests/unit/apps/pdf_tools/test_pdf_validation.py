"""P0 regression: every PDF entry point validates size/validity."""
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from apps.pdf_tools.serializers import (
    ImagesToPdfSerializer,
    PdfCompressSerializer,
    PdfMergeSerializer,
    PdfProtectSerializer,
    PdfRotateSerializer,
    PdfSplitSerializer,
    PdfToImageSerializer,
    PdfUnlockSerializer,
    validate_pdf_upload,
)


def _pdf_bytes(encrypt_password=None):
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    if encrypt_password:
        writer.encrypt(encrypt_password)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _pdf_file(name="a.pdf", password=None):
    return SimpleUploadedFile(name, _pdf_bytes(password), content_type="application/pdf")


class TestValidatePdfUpload:
    def test_valid_pdf_passes(self):
        assert validate_pdf_upload(_pdf_file()).size > 0

    def test_oversize_rejected(self):
        class Big:
            size = 26 * 1024 * 1024

            def seek(self, *a):
                pass

        with pytest.raises(serializers.ValidationError):
            validate_pdf_upload(Big())

    def test_non_pdf_rejected(self):
        bad = SimpleUploadedFile("a.pdf", b"not a pdf at all", content_type="application/pdf")
        with pytest.raises(serializers.ValidationError):
            validate_pdf_upload(bad)

    def test_encrypted_rejected_by_default(self):
        with pytest.raises(serializers.ValidationError):
            validate_pdf_upload(_pdf_file(password="secret"))

    def test_encrypted_allowed_with_flag(self):
        assert validate_pdf_upload(_pdf_file(password="secret"), allow_encrypted=True)


class TestSerializerCoverage:
    def test_merge_validates_each_file(self):
        s = PdfMergeSerializer(data={"files": [_pdf_file("a.pdf"), _pdf_file("b.pdf")]})
        assert s.is_valid(), s.errors

    def test_merge_rejects_non_pdf(self):
        bad = SimpleUploadedFile("x.pdf", b"nope", content_type="application/pdf")
        s = PdfMergeSerializer(data={"files": [bad]})
        assert not s.is_valid()

    def test_split_compress_rotate_validate(self):
        assert PdfSplitSerializer(data={"file": _pdf_file(), "pages": "1"}).is_valid()
        assert PdfCompressSerializer(data={"file": _pdf_file()}).is_valid()
        assert PdfRotateSerializer(data={"file": _pdf_file(), "degree": 90}).is_valid()

    def test_split_rejects_encrypted(self):
        s = PdfSplitSerializer(data={"file": _pdf_file(password="s"), "pages": "1"})
        assert not s.is_valid()

    def test_protect_unlock_accept_encrypted(self):
        assert PdfProtectSerializer(
            data={"file": _pdf_file(password="s"), "password": "newpass"}
        ).is_valid()
        assert PdfUnlockSerializer(
            data={"file": _pdf_file(password="s"), "password": "s"}
        ).is_valid()

    def test_to_image_rejects_encrypted(self):
        assert not PdfToImageSerializer(data={"file": _pdf_file(password="s")}).is_valid()

    def test_images_reject_oversize(self):
        from types import SimpleNamespace

        s = ImagesToPdfSerializer()
        big = SimpleNamespace(size=26 * 1024 * 1024, seek=lambda *a: None)
        with pytest.raises(serializers.ValidationError):
            s.validate_images([big])

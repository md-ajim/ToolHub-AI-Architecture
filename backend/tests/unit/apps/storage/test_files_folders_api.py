"""Phase 1/2 regression: storage upload/download/assign + folders CRUD.

Unittest-style (Django runner compatible — no pytest import).
Covers spec §40: upload, folder creation, file validation.
"""
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apps.storage.models import File
from apps.workspace.models import Folder, Project

User = get_user_model()


class StorageUploadDownloadTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="files@example.com", password="TestPass123!")
        self.other = User.objects.create_user(email="other@example.com", password="TestPass123!")
        self.client.force_authenticate(self.user)

    def _upload(self, name="hello.txt", content=b"hello world", **extra):
        data = {"file": SimpleUploadedFile(name, content, content_type="text/plain"), **extra}
        return self.client.post("/api/v1/storage/files/", data, format="multipart")

    def test_upload_creates_real_file_row(self):
        res = self._upload()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        body = res.data["data"]
        self.assertEqual(body["filename"], "hello.txt")
        self.assertTrue(File.objects.filter(pk=body["id"], user=self.user).exists())

    def test_upload_rejects_executable(self):
        res = self._upload(name="run.exe", content=b"MZ")
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(File.objects.filter(user=self.user).exists())

    def test_upload_requires_file(self):
        res = self.client.post("/api/v1/storage/files/", {}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_returns_identical_bytes(self):
        up = self._upload(content=b"byte-exact-content")
        file_id = up.data["data"]["id"]
        res = self.client.get(f"/api/v1/storage/files/{file_id}/download/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        content = b"".join(res.streaming_content)
        self.assertEqual(content, b"byte-exact-content")

    def test_download_foreign_file_is_404(self):
        up = self._upload()
        file_id = up.data["data"]["id"]
        self.client.force_authenticate(self.other)
        res = self.client.get(f"/api/v1/storage/files/{file_id}/download/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_assigns_folder_and_project(self):
        folder_res = self.client.post("/api/v1/workspace/folders/", {"name": "Work"}, format="json")
        project_res = self.client.post("/api/v1/workspace/projects/", {"name": "Site"}, format="json")
        up = self._upload()
        file_id = up.data["data"]["id"]
        res = self.client.patch(
            f"/api/v1/storage/files/{file_id}/",
            {"folder_id": folder_res.data["data"]["id"], "project_id": project_res.data["data"]["id"]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        row = File.objects.get(pk=file_id)
        self.assertEqual(str(row.folder_id), folder_res.data["data"]["id"])
        self.assertEqual(str(row.project_id), project_res.data["data"]["id"])

    def test_patch_rejects_foreign_folder(self):
        self.client.force_authenticate(self.other)
        foreign = self.client.post("/api/v1/workspace/folders/", {"name": "Theirs"}, format="json")
        self.client.force_authenticate(self.user)
        up = self._upload()
        res = self.client.patch(
            f"/api/v1/storage/files/{up.data['data']['id']}/",
            {"folder_id": foreign.data["data"]["id"]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class FolderCrudTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="folders@example.com", password="TestPass123!")
        self.client.force_authenticate(self.user)

    def test_create_and_list_folder(self):
        res = self.client.post("/api/v1/workspace/folders/", {"name": "Design"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("file_count", res.data["data"])
        listed = self.client.get("/api/v1/workspace/folders/")
        self.assertEqual(len(listed.data["data"]), 1)

    def test_create_requires_name(self):
        res = self.client.post("/api/v1/workspace/folders/", {"name": "  "}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nested_and_cycle_guard(self):
        parent = self.client.post("/api/v1/workspace/folders/", {"name": "P"}, format="json").data["data"]
        child = self.client.post(
            "/api/v1/workspace/folders/", {"name": "C", "parent": parent["id"]}, format="json"
        ).data["data"]
        # Moving the parent under its own child must be refused.
        res = self.client.patch(
            f"/api/v1/workspace/folders/{parent['id']}/", {"parent": child["id"]}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Folder.objects.filter(pk=parent["id"], parent__isnull=True).exists())

    def test_delete_unfiles_contained_files(self):
        folder_id = self.client.post("/api/v1/workspace/folders/", {"name": "Tmp"}, format="json").data["data"]["id"]
        up = self.client.post(
            "/api/v1/storage/files/",
            {"file": SimpleUploadedFile("a.txt", b"a"), "folder_id": folder_id},
            format="multipart",
        )
        file_id = up.data["data"]["id"]
        res = self.client.delete(f"/api/v1/workspace/folders/{folder_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        row = File.objects.get(pk=file_id)
        self.assertIsNone(row.folder_id)
        self.assertTrue(Folder.objects.filter(pk=folder_id, deleted_at__isnull=False).exists())


class ProjectUpdateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="proj@example.com", password="TestPass123!")
        self.client.force_authenticate(self.user)

    def test_patch_renames_project(self):
        created = self.client.post("/api/v1/workspace/projects/", {"name": "Old"}, format="json").data["data"]
        res = self.client.patch(
            f"/api/v1/workspace/projects/{created['id']}/",
            {"name": "New", "description": "d"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["data"]["name"], "New")
        self.assertTrue(Project.objects.filter(pk=created["id"], name="New").exists())

    def test_patch_rejects_empty_name(self):
        created = self.client.post("/api/v1/workspace/projects/", {"name": "Keep"}, format="json").data["data"]
        res = self.client.patch(
            f"/api/v1/workspace/projects/{created['id']}/", {"name": "  "}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

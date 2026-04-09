from django.contrib.auth import get_user_model
from django.test import TestCase

from config.enums import NodeType
from files.models import FileBlob, Node
from files.services import file_service

User = get_user_model()


class NodeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            is_active=True,
            email_verified=True,
        )

    def test_build_path(self):
        root = Node.objects.create(owner=self.user, name="root", ext="", node_type=NodeType.FOLDER)
        parent = Node.objects.create(owner=self.user, name="parent", ext="", node_type=NodeType.FOLDER, parent=root)
        file_node = Node.objects.create(owner=self.user, name="file.txt", ext=".txt", node_type=NodeType.FILE, parent=parent)

        self.assertEqual(root.path, "/root")
        self.assertEqual(parent.path, "/root/parent")
        self.assertEqual(file_node.path, "/root/parent/file.txt")

    def test_move_folder_updates_child_paths(self):
        root = Node.objects.create(owner=self.user, name="root", ext="", node_type=NodeType.FOLDER)
        parent = Node.objects.create(owner=self.user, name="parent", ext="", node_type=NodeType.FOLDER, parent=root)
        folder = Node.objects.create(owner=self.user, name="folder", ext="", node_type=NodeType.FOLDER, parent=root)
        child = Node.objects.create(owner=self.user, name="child.txt", ext=".txt", node_type=NodeType.FILE, parent=folder)

        folder.move(new_parent=parent)

        folder.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(folder.path, "/root/parent/folder")
        self.assertEqual(child.path, "/root/parent/folder/child.txt")

    def test_move_folder_to_descendant_raises_error(self):
        root = Node.objects.create(owner=self.user, name="root", ext="", node_type=NodeType.FOLDER)
        child = Node.objects.create(owner=self.user, name="child", ext="", node_type=NodeType.FOLDER, parent=root)

        with self.assertRaises(ValueError):
            root.move(new_parent=child)


class FileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test2@example.com",
            password="password",
            is_active=True,
            email_verified=True,
        )
        self.root = Node.objects.create(owner=self.user, name="root", ext="", node_type=NodeType.FOLDER)
        self.file_node = Node.objects.create(
            owner=self.user,
            name="doc.txt",
            ext=".txt",
            node_type=NodeType.FILE,
            parent=self.root,
        )

    def test_create_folder_sets_empty_extension(self):
        folder = file_service.create_folder(self.user, "reports", parent=self.root)

        self.assertEqual(folder.ext, "")
        self.assertEqual(folder.node_type, NodeType.FOLDER)

    def test_move_to_trash_sets_deleted_at(self):
        file_service.move_to_trash(self.file_node)
        self.file_node.refresh_from_db()

        self.assertTrue(self.file_node.trashed)
        self.assertIsNotNone(self.file_node.deleted_at)

    def test_restore_clears_deleted_at(self):
        file_service.move_to_trash(self.file_node)
        file_service.restore_file(self.file_node)
        self.file_node.refresh_from_db()

        self.assertFalse(self.file_node.trashed)
        self.assertIsNone(self.file_node.deleted_at)


class FileBlobModelTests(TestCase):
    def test_size_mb_handles_none(self):
        blob = FileBlob(size=None)
        self.assertIsNone(blob.size_mb())

    def test_size_mb_rounds_megabytes(self):
        blob = FileBlob(size=2 * 1024 * 1024)
        self.assertEqual(blob.size_mb(), 2.0)

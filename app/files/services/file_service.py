from django.utils import timezone
from django.db.models import Q
from files.models import Node, NodeType
from files.services.storage import save_file, validate_upload

def get_user_files(user, q=None, parent_id=None):
    qs = Node.objects.filter(owner=user, trashed=False).order_by("-created_at")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    else:
        if parent_id:
            # Frontend sends UUID as parent_id
            qs = qs.filter(parent__uid=parent_id)
        else:
            qs = qs.filter(parent__isnull=True)
    return qs

def create_folder(user, name, parent=None):
    return Node.objects.create(owner=user, name=name, ext="", node_type=NodeType.FOLDER, parent=parent)

def toggle_star_status(node):
    node.starred = not node.starred
    node.save()
    return node.starred

def move_to_trash(node):
    node.trashed = True
    node.deleted_at = timezone.now()
    node.save(update_fields=["trashed", "deleted_at", "path", "updated_at"])
    return node

def get_recent_files(user, limit=20):
    return Node.objects.filter(owner=user, node_type=NodeType.FILE, trashed=False).order_by("-updated_at")[:limit]

def get_starred_files(user):
    return Node.objects.filter(owner=user, starred=True, trashed=False).order_by("-created_at")

def get_trashed_files(user):
    return Node.objects.filter(owner=user, trashed=True).order_by("-deleted_at")

def restore_file(node):
    node.trashed = False
    node.deleted_at = None
    node.save(update_fields=["trashed", "deleted_at", "path", "updated_at"])
    return node

def permanent_delete(node):
    node.delete()

def empty_trash(user):
    Node.objects.filter(owner=user, trashed=True).delete()

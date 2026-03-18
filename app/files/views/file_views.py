from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from files.models import UserFile
from files.forms import UploadFileForm

from accounts.decorators import email_verification_required

# logging
import logging
logger = logging.getLogger(__name__)

@login_required
@email_verification_required
def file_list(request):
    q = (request.GET.get("q", "")).strip() # query
    qs = UserFile.objects.filter(owner=request.user).order_by("-created_at")

    if q:
        qs = qs.filter(Q(original_name__icontains=q) | Q(description__icontains=q))
    return render(request, "files/file_list.html", {"files": qs, "q": q})


from files.services import save_file, validate_upload
@login_required
@email_verification_required
@require_http_methods(["POST", "GET"])
def upload_file(request):
    logger.info("upload file view")
    logger.info(request)

    if request.method == "GET":
        return render(request, "files/upload.html", {
            "form": UploadFileForm()
        })

    result = validate_upload(request.user, request.FILES["file"])

    if not result.ok:
        return JsonResponse({
            "ok": False,
            "status": "error",
            "errors": result.errors,
        }, status=400)

    try:
        obj = save_file(
            owner=request.user,
            file=request.FILES["file"],
            description=request.POST.get("description", ""),
        )
        return JsonResponse({
            "ok": True,
            "status": "duplicate" if result.duplicate else "done",
            "file_id": obj.id,
            "name": obj.original_name,
            "warnings": result.warnings
        })

    except Exception as e:
        logger.exception("uploading file failed")
        return JsonResponse({
            "ok": False,
            "status": "error",
            "errors": [str(e)],
        }, status=500)


def _get_file_with_name(owner, original_name):
    return UserFile.objects.filter(
        owner=owner,
        original_name=original_name,
    )

def _get_same_name_exists(owner, original_name):
    return UserFile.objects.filter(
        owner=owner,
        original_name=original_name,
    ).exists()


def toggle_star(request, pk: int):
    uf = get_object_or_404(UserFile, pk=pk, owner=request.user)
    uf.starred = not uf.starred
    uf.save()
    return redirect("files:list")


@login_required
def file_detail(request, pk: int):
    uf = get_object_or_404(UserFile, pk=pk, owner=request.user)
    return render(request, "files/detail.html", {"f": uf})

@login_required
def file_download(request, pk: int):
    uf = get_object_or_404(UserFile, pk=pk, owner=request.user)
    if not uf.file:
        raise Http404
    resp = FileResponse(uf.file.open("rb"), as_attachment=True, file_name=uf.original_name)
    resp.headers["Content-Disposition"] += f'; filename="{uf.original_name}"'
    return resp

@login_required
def file_delete(request, pk: int):
    uf = get_object_or_404(UserFile, pk=pk, owner=request.user)
    if not uf.file:
        raise Http404
    if request.method == "POST":
        uf.file.delete(save=False)
        uf.delete()
        return redirect("files:list")
    return render(request, "files/delete.html", {"f": uf})


@login_required
@email_verification_required
def recent_files(request):
    qs = UserFile.objects.filter(owner=request.user).order_by("-updated_at")
    return render(request, "files/file_list.html", {"files": qs})


@login_required
@email_verification_required
def starred_files(request):
    qs = UserFile.objects.filter(owner=request.user, starred=True).order_by("-created_at")
    return render(request, "files/starred_files.html", {"files": qs})

@login_required
@email_verification_required
def trash_files(request):
    qs = UserFile.objects.filter(owner=request.user, trashed=True).order_by("-deleted_at")
    return render(request, "files/trash_files.html", {"files": qs})
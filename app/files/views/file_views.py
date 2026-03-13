from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from files.models import UserFile
from files.forms import UploadFileForm

# logging
import logging
logger = logging.getLogger(__name__)

@login_required
def file_list(request):
    q = (request.GET.get("q", "")).strip() # query
    qs = UserFile.objects.filter(owner=request.user).order_by("-uploaded_at")

    if q:
        qs = qs.filter(Q(original_name__icontains=q) | Q(description__icontains=q))
    return render(request, "files/list.html", {"files": qs, "q": q})


from files.services import save_file
@login_required
def upload_file(request):

    logger.info("upload file view")
    logger.info(request)

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                uploaded_file = request.FILES["file"]
                save_file(
                    owner=request.user,
                    file=uploaded_file,
                    description=form.cleaned_data["description"]
                )
                messages.success(request, "파일 업로드 완료")
                return redierect("files:list")
            except Exception:
                logger.exception("upload_file failed for user_id=%s", request.user.id)
                messages.error(request, "파일 업로드 중 문제가 발생")
    else:
        form = UploadFileForm()

    return render(request, "files/upload.html", {"form": form})


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

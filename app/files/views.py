from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from .models import UserFile
from .forms import UploadFileForm

from pathlib import Path
import json
DUMMY_PATH = Path(__file__).resolve().parent / "dummy_files.json"

def load_dummy_files() -> list[dict]:
    if not DUMMY_PATH.exists():
        return []
    return json.loads(DUMMY_PATH.read_text(encoding="utf-8"))

def save_dummy_files(data: list[dict]) -> None:
    DUMMY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_dummy_files(item: dict) -> dict:
    data = load_dummy_files()
    
    existing_ids = {d.get("id") for d in data if "id" in d}
    if item.get("id") is None:
        next_id = (max(existing_ids or [0]) + 1)
        item["id"] = next_id
    elif item["id"] in existing_ids:
        raise ValueError(f"ID {item['id']} 중복")
    
    data.append(item)
    save_dummy_files(data)
    return item

def extend_dummy_files(item: list[dict]) -> list[dict]:
    data = load_dummy_files()
    
    existing_ids = {d.get("id") for d in data if "id" in d}
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    for i in item:
        if i.get("id") is None:
            i["id"] = next_id
            next_id += 1
        elif i["id"] in existing_ids:
            raise ValueError(f"ID {i['id']} 중복")
        existing_ids.add(i["id"])
        data.append(i)

    save_dummy_files(data)
    return item


@login_required
def dummy_file_list(request):
    q = (request.GET.get("q", "")).strip() # query
    qs = load_dummy_files()

    if q:
        ql = q.lower()
        qs = [f for f in qs if ql in f.get("name", "").lower() or ql in f.get("desc", "").lower()]
    return render(request, "files/list.html", {"files": qs, "q": q})


@login_required
@require_http_methods(["GET", "POST"])
def edit_dummy_file(request):
    if request.method == "POST":
        raw = request.POST.get("json_text", "")
        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError("리스트로 내놔")
            if len(data) == 1:
                append_dummy_files(data[0])
            else:
                extend_dummy_files(data)
            messages.success(request, "저장 굳")
            return redirect("files:list")
        except Exception as e:
            messages.error(request, str(e))
            return render(request, "files/list.html", {"files": None, "q": ""})
    else:
        data = load_dummy_files()
        return render(
            request,
            "files/list.html",
            {"files": data, "q": ""}
        )
    return render(
        request,
        "files/list.html",
        {"files": None, "q": ""}
    )


@login_required
def file_list(request):
    q = (request.GET.get("q", "")).strip() # query
    qs = UserFile.objects.filter(owner=request.user).order_by("-uploaded_at")

    if q:
        qs = qs.filter(Q(original_name__icontains=q) | Q(description__icontains=q))
    return render(request, "files/list.html", {"files": qs, "q": q})

@login_required
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uf = form.save(commit=False)
            uf.owner = request.user
            uf.original_name = request.FILES["file"].name
            uf.size = request.FILES["file"].size
            uf.save()
            return redirect("file:list")
    else:
        form = UploadFileForm()
    return render(request, "files/upload.html", {"form": form})

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
        return redirect("file:list")
    return render(request, "files/delete.html", {"f": uf})


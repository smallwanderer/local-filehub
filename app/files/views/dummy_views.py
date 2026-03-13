import json
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.shortcuts import render, redirect

DUMMY_PATH = Path(__file__).resolve().parent.parent / "dummy_files.json"

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

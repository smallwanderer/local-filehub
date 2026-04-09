from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import email_verification_required
from files.models import Node, NodeType

@login_required
@email_verification_required
def index(request):
    """ 메인 파일 목록 뷰 (빈 틀 반환) """
    return render(request, "files/file_list.html")

@login_required
@email_verification_required
def node_view(request, uid):
    """ 노드(파일/폴더) 상세 뷰 """
    node = get_object_or_404(Node, uid=uid, owner=request.user)

    # 브레드크럼 빌드
    breadcrumbs = []
    current = node
    while current:
        breadcrumbs.insert(0, {"uid": str(current.uid), "name": current.name})
        current = current.parent

    if node.node_type == NodeType.FOLDER:
        return render(request, "files/file_list.html", {
            "current_folder": node,
            "current_folder_uid": str(node.uid),
            "current_folder_name": node.name,
            "breadcrumbs": breadcrumbs,
        })
    else:
        return render(request, "files/file_detail.html", {
            "file": node,
            "breadcrumbs": breadcrumbs,
        })

@login_required
@email_verification_required
def upload(request):
    """ 파일 업로드 뷰 """
    return render(request, "files/upload.html")

@login_required
@email_verification_required
def recent(request):
    return render(request, "files/recent_files.html")

@login_required
@email_verification_required
def starred(request):
    return render(request, "files/starred_files.html")

@login_required
@email_verification_required
def trash(request):
    return render(request, "files/trash_files.html")


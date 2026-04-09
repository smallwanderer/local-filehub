from celery import Celery
import os

# 이 부분은 'celery' program 구동을 위한 Default Django settings module을 setting합니다.
# 이 줄은 필요하지 않지만 항상 설정 모듈을 셀러리 프로그램으로 전달하는 것을 방지합니다.
# 앱 인스턴스를 생성하기 전에 다음 작업을 수행해야 합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# 여기서 문자열을 사용하면 작업자가 구성 개체를 하위 프로세스에 직렬화할 필요가 없습니다.
# 네임스페이스='CELERY'는 모든 셀러리 관련 구성 키에 'CELERY_' 접두사가 있어야 함을 의미합니다.
app.config_from_object("django.conf:settings", namespace="CELERY")

# 앱의 tasks.py 파일을 자동으로 검색합니다.
app.autodiscover_tasks()
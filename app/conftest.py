import django
from django.conf import settings

def pytest_configure():
    settings.configure(
        # 최소한의 설정으로 Django를 초기화합니다.
        # 실제 DB 연결 등은 필요하지 않으므로 최소한으로 설정합니다.
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            # 테스트에 필요한 앱만 추가하거나 비워둡니다.
            # 'django.contrib.auth',
            # 'django.contrib.contenttypes',
        ],
        # 기타 필요한 설정이 있다면 추가합니다.
        # SECRET_KEY='dummy-key',
    )
    django.setup()

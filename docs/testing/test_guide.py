"""
TEST ISHGA TUSHIRISH VA NATIJALARNI TUSHUNISH
==============================================

Bu fayl sizga testlarni qanday ishga tushirish va natijalarni
qanday tahlil qilishni o'rgatadi.
"""

# ========================================
# 1. TESTLARNI ISHGA TUSHIRISH
# ========================================

"""
ASOSIY BUYRUQLAR:

1. Barcha testlarni ishga tushirish:
   $ pytest

2. Ma'lum bir faylni test qilish:
   $ pytest tests/users/test_registration.py

3. Ma'lum bir testni ishga tushirish:
   $ pytest tests/users/test_registration.py::TestUserRegistration::test_successful_registration

4. Ma'lum marker bilan testlarni ishga tushirish:
   $ pytest -m unit          # Faqat unit testlar
   $ pytest -m integration   # Faqat integration testlar
   $ pytest -m "not slow"    # Sekin testlarni skip qilish

5. Verbose rejimda (ko'proq ma'lumot):
   $ pytest -v
   $ pytest -vv  # Juda ko'p ma'lumot

6. Test coverage bilan:
   $ pytest --cov=apps
   $ pytest --cov=apps --cov-report=html

7. Failed testlarni qayta ishga tushirish:
   $ pytest --lf  # last-failed
   $ pytest --ff  # failed-first

8. Parallel test (tezroq):
   $ pytest -n auto  # (pytest-xdist kerak)
"""


# ========================================
# 2. TEST NATIJALARINI O'QISH
# ========================================

"""
PYTEST OUTPUT TUSHUNTIRISH:

✅ PASSED natija:
========================= test session starts =========================
platform linux -- Python 3.10.12, pytest-8.0.0
collected 5 items

tests/users/test_registration.py .....                         [100%]

========================= 5 passed in 2.34s ===========================

- "." - har bir test o'tdi
- "5 passed" - 5 ta test muvaffaqiyatli
- "in 2.34s" - 2.34 sekundda tugadi


❌ FAILED natija:
========================= test session starts =========================
collected 5 items

tests/users/test_registration.py ..F..                         [100%]

============================== FAILURES ===============================
___________ TestUserRegistration.test_password_mismatch ______________

    def test_password_mismatch(api_client):
        response = api_client.post(url, data)
>       assert response.status_code == 400
E       AssertionError: assert 201 == 400

tests/users/test_registration.py:45: AssertionError
========================= 1 failed, 4 passed in 2.45s ================

- "F" - failed test
- AssertionError - nima xato bo'lgan
- 201 != 400 - kutilgan 400, lekin 201 keldi


⚠️ SKIPPED natija:
tests/users/test_registration.py s                             [100%]

========================= 1 skipped in 0.05s ==========================

- "s" - test skip qilindi (pytest.skip())


❗ ERROR natija:
tests/users/test_registration.py E                             [100%]

============================== ERRORS =================================
___________ ERROR at setup of test_something _________________________
...
- "E" - test o'zida xato (setup/teardown da xato)
"""


# ========================================
# 3. COVERAGE REPORTINI TUSHUNISH
# ========================================

"""
COVERAGE REPORT:

$ pytest --cov=apps --cov-report=term-missing

Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
apps/users/models.py                      45      5    89%    23-27
apps/users/views.py                      120     30    75%    45-50, 78-82
apps/users/serializers.py                 80     10    88%    67-70
apps/users/services/auth_service.py       50      0   100%
---------------------------------------------------------------------
TOTAL                                    295     45    85%

TUSHUNTIRISH:
- Stmts (Statements): Jami kod satrlari
- Miss (Missed): Test qilinmagan satrlar
- Cover (Coverage): Test qilingan foiz
- Missing: Qaysi satrlar test qilinmagan

YAXSHI COVERAGE:
- 70%+  : Yaxshi
- 80%+  : Juda yaxshi
- 90%+  : A'lo
- 100%  : Mukammal (lekin har doim ham mumkin emas)


HTML REPORT:
$ pytest --cov=apps --cov-report=html

Bu htmlcov/ papkada HTML report yaratadi.
htmlcov/index.html ni brauzerda oching - juda ko'rish qulay!
"""


# ========================================
# 4. KENG TARQALGAN XATOLAR VA YECHIMLAR
# ========================================

"""
XATO 1: ModuleNotFoundError
----------------------------
ERROR: ModuleNotFoundError: No module named 'apps.users'

YECHIM:
- PYTHONPATH to'g'ri sozlanganini tekshiring
- pytest.ini da DJANGO_SETTINGS_MODULE to'g'ri ko'rsatilganini tekshiring
- Virtual environment faollashtirilganini tekshiring


XATO 2: Database errors
-----------------------
ERROR: django.db.utils.OperationalError: no such table: users_user

YECHIM:
- Migratsiyalarni ishga tushiring:
  $ python manage.py migrate
- Test database yaratish uchun:
  $ pytest --create-db


XATO 3: Import errors
---------------------
ERROR: ImportError: cannot import name 'UserFactory'

YECHIM:
- Factory yaratilganini tekshiring
- __init__.py fayllar borligini tekshiring
- Import path to'g'ri yozilganini tekshiring


XATO 4: Fixture not found
--------------------------
ERROR: fixture 'user' not found

YECHIM:
- conftest.py faylida fixture aniqlangan bo'lishi kerak
- conftest.py to'g'ri joyda (tests/ papkada)
- Fixture nomi to'g'ri yozilgan


XATO 5: Authentication errors
------------------------------
ERROR: AssertionError: assert 401 == 200

YECHIM:
- authenticated_client fixture ishlatilganini tekshiring
- Token to'g'ri generatsiya qilinganini tekshiring
- Permission class to'g'ri sozlanganini tekshiring
"""


# ========================================
# 5. TEST YOZISHDA BEST PRACTICES
# ========================================

"""
✅ QILISH KERAK:

1. Test nomlarini tushunarli qiling
   ✅ def test_user_can_login_with_valid_credentials()
   ❌ def test1()

2. AAA pattern ishlatilsin
   - Arrange (tayyorlash)
   - Act (harakat qilish)
   - Assert (tekshirish)

3. Har bir test faqat BITTA narsani tekshirsin
   ✅ test_registration_success
   ✅ test_registration_invalid_email
   ❌ test_registration_everything  # Hamma narsani

4. Fixture'larni qayta ishlating
   ✅ def test_something(user, api_client)
   ❌ def test_something():
        user = User.objects.create(...)

5. Mock'ni to'g'ri ishlating
   ✅ Email/SMS/To'lov gateway
   ❌ Database operatsiyalar

6. Test data fixture/factory orqali yarating
   ✅ user = UserFactory()
   ❌ user = User.objects.create(email='test@...')

7. Assertion message yozing
   ✅ assert status == 200, f"Expected 200, got {status}"
   ❌ assert status == 200


❌ QILMASLIK KERAK:

1. Test tartibiga bog'liq testlar
   ❌ test_1 test_2 ga bog'liq

2. Test'lar bir-biriga ta'sir qilishi
   ❌ test_1 database'ni o'zgartirdi, test_2 bunga bog'liq

3. Juda ko'p assertion bitta testda
   ❌ 10 ta assert bitta test ichida

4. Real API/Service'larga so'rov yuborish
   ❌ requests.get('https://real-api.com')

5. Hard-coded ma'lumotlar
   ❌ user_id = 123
   ✅ user_id = user.id

6. Sleep() ishlatish
   ❌ time.sleep(5)
   ✅ Mock yoki async wait
"""


# ========================================
# 6. KEYINGI QADAMLAR
# ========================================

"""
KELING BIRGALIKDA:

1. ✅ Testlarni ishga tushiramiz
   $ pytest -v

2. ✅ Xatolarni topamiz va tuzatamiz
   - Import xatolari
   - URL routing
   - Assertion xatolari

3. ✅ Coverage reportini ko'ramiz
   $ pytest --cov=apps --cov-report=html

4. ✅ Qolgan User endpoints uchun testlar yozamiz
   - Login
   - Logout
   - Password reset
   - Email verification

5. ✅ 70%+ coverage ga erishamiz

6. ✅ Products moduliga o'tamiz (TDD bilan)
"""
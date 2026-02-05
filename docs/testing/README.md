# Testing Documentation

Bu papkada testing bilan bog'liq o'rganish materiallari joylashgan.

## Fayllar

### 1. `test_guide.py`
Testlarni qanday ishga tushirish va natijalarni qanday tushunish haqida batafsil qo'llanma.

**Mavzular:**
- Test buyruqlari (`pytest -v`, `pytest --cov`, va h.k.)
- Test natijalarini o'qish
- Coverage reportlarini tushunish
- Keng tarqalgan xatolar va yechimlar
- Best practices

### 2. `mock_examples.py`
Mock konseptini chuqur tushuntirish va amaliy misollar.

**Mavzular:**
- Mock nima va nima uchun kerak?
- Email yuborishni mock qilish
- To'lovni mock qilish
- Vaqtni mock qilish
- Mock metodlari (`patch`, `return_value`, `side_effect`)
- Qachon mock ishlatish kerak

### 3. `parametrize_examples.py`
Pytest parametrize funksiyasi va uning qo'llanilishi.

**Mavzular:**
- Parametrize nima?
- Bir testni turli ma'lumotlar bilan ishlatish
- Email validation testlari
- Password strength testlari
- Multiple parametrlar
- Real loyiha misollari

## Qanday Foydalanish

Bu fayllar **o'rganish uchun** - ular testlarni ishga tushirmaydi, lekin konseptlarni tushunishga yordam beradi.

### O'qish tartibi:
1. `test_guide.py` - Boshidan boshlang
2. `mock_examples.py` - Mock konseptini o'rganing
3. `parametrize_examples.py` - Advanced patterns

## Qo'shimcha Resurslar

### Official Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)

### Books
- "Test-Driven Development with Python" - Harry Percival
- "Python Testing with pytest" - Brian Okken

### Online Courses
- Real Python - pytest course
- Test Automation University

## Contributors

Bu materiallar loyihani test qilish jarayonida to'plangan bilimlar asosida yaratilgan.

## License

Educational materials - free to use and modify.
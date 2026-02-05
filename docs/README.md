# E-commerce API Documentation

Bu papka loyiha hujjatlari va o'rganish materiallarini o'z ichiga oladi.

## Dokumentatsiya Strukturasi

```
docs/
├── testing/              # Testing hujjatlari
│   ├── README.md        # Testing guide
│   ├── mock_examples.py
│   ├── parametrize_examples.py
│   └── test_guide.py
│
└── README.md            # Siz hozir shu faylni o'qiyapsiz
```

## Maqsad

Ushbu hujjatlar quyidagilar uchun:

1. **O'rganish** - Yangi texnologiyalar va konseptlarni tushunish
2. **Reference** - Tez ma'lumot topish
3. **Best Practices** - Professional yondashuvlarni o'rganish
4. **Onboarding** - Yangi developerlar uchun qo'llanma

## Bo'limlar

### Testing Documentation
Testlar yozish, ishga tushirish va maintain qilish bo'yicha to'liq qo'llanma.

**Joylashuv:** `docs/testing/`

**Mavzular:**
- Pytest asoslari
- Mock va Fixtures
- Test-Driven Development
- Coverage optimization
- Best practices

## Qo'llanma

### Yangi Developerlar Uchun

1. **Boshlash:**
   ```bash
   # Virtual environment yarating
   python -m venv venv
   venv\Scripts\activate  # Windows
   
   # Dependencies o'rnating
   pip install -r requirements.txt
   
   # Testlarni ishga tushiring
   pytest -v
   ```

2. **O'rganish:**
   - `docs/testing/test_guide.py` - Testlar bilan ishlash
   - `docs/testing/mock_examples.py` - Mock konseptini o'rganish
   - `docs/testing/parametrize_examples.py` - Advanced patterns

3. **Amaliyot:**
   - `tests/` papkadagi real testlarni o'rganing
   - Yangi testlar yozing
   - Coverage'ni oshiring

## Contributing

Hujjatlarni yaxshilash uchun:

1. Yangi qo'llanma yozing
2. Mavjudlarini yangilang
3. Misollar qo'shing
4. Pull Request yuboring

## Foydali Linklar

### Loyiha
- [Main README](../README.md)
- [API Documentation](http://localhost:8000/api/docs/)
- [Test Coverage Report](../htmlcov/index.html)

### External Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Savol va Takliflar

Agar savol yoki taklifingiz bo'lsa:
- GitHub Issue oching
- Pull Request yuboring
- Team bilan muhokama qiling

---

**Last Updated:** 2026-02-05
**Version:** 1.0.0
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
  """
    Custom User Admin Panel
    
    Qismlar:
    1. list_display - jadvalda ko'rinadigan ustunlar
    2. list_filter - o'ng tarafdagi filterlar
    3. search_fields - qidiruv maydonlari
    4. ordering - saralash
    5. fieldsets - detail page layout (edit)
    6. add_fieldsets - yangi user qo'shish layout
  """
  list_display = [
    'email',
    'get_full_name_display',
    'phone_number',
    'is_active_display',
    'is_staff',
    'date_joined_display',
  ]

  list_filter = [
    'is_active',
    'is_staff',
    'is_superuser',
    'date_joined',
  ]

  search_fields = [
    'email',
    'first_name',
    'last_name',
    'phone_number',
  ]

  ordering = ['-date_joined']

  fieldsets = (
    # Bo'lim 1: Login ma'lumotlari
    ('autentifikansiya', {
      'fields': ('email', 'password')
    }),
    # Bo'lim 2: Shaxsiy
    ('Shahsiy ma\'lumotlar', {
      'fields': ('first_name', 'last_name', 'phone_number'),
      'description': 'Foydalanuvchi shaxsiy ma\'lumotlari' 
    }),
    # Bo'lim 3: Manzil (Yopiq boshlanadi)
    ('Manzil', {
      'fields': ('address', 'city', 'country', 'postal_code'),
      'classes': ('collapse',),
    }),
    # Bo'lim 4: Ruxsatlar (Yopiq)
    ('Ruxsatlar', {
      'fields': (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
        'user_permissions'
      ),
      'classes': ('collapse',),
    }),
    # Bo'lim 5: Tarix (O'qish uchun)
    ('Tarix', {
      'fields': ('date_joined', 'last_login'),
      'classes': ('collapse',),
    }),
  )

  add_fieldsets = (
      ('Yangi foydalanuvchi yaratish', {
      'classes': ('wide',),
      'fields': (
        'email',
        'password1',
        'password2',
        'first_name',
        'last_name',
        'phone_number',
        'is_active',
        'is_staff',
      ),
    }),
  )

  readonly_fields = ['date_joined', 'last_login']

  # ==================== CUSTOM METODLAR ====================
  @admin.display(description="To'liq ism", ordering='first_name')
  def get_full_name_display(self, obj):
    """
      Jadvalda to'liq ismni ko'rsatish
      
      Args:
          obj: User obyekti (har bir qator)
      
      Returns:
          HTML yoki string
    """
    full_name = obj.get_full_name()

    if full_name == obj.email:
      return format_html(
          '<span style="color: gray; font-style: italic;">{}</span>',
          "Ism kiritilmagan"
      )
    return full_name

  @admin.display(description='Status', boolean=True)
  def is_active_display(self, obj):
    """
      Active holatni icon bilan ko'rsatish
      
      boolean=True → Django avtomatik ✓ yoki ✗ qo'yadi
    """
    return obj.is_active

  @admin.display(description="Ro'yxatdan o'tgan", ordering='data_joined')
  def date_joined_display(self, obj):
    """
      Sanani o'zbek formatida ko'rsatish
      
      Returns:
          "27.01.2026 15:30"
    """
    return obj.date_joined.strftime('%d.%m.%Y %H:%M')

  # ==================== ACTIONS ====================
  actions = ['activate_users', 'deactivate_users']

  @admin.display(description="Tanlangan userlarni faollashtirish")
  def activate_users(self, request, queryset):
    """
      Bir nechta userni bir vaqtda activate qilish
      
      Args:
          request: HTTP request
          queryset: Tanlangan userlar
    """
    updated = queryset.update(is_active=True)

    self.message_user(
      request,
      f"{updated} ta foydalanuvchi faollashtirildi.",
      level='success'
    )

  @admin.display(description="Tanlangan userlarni bloklash")
  def deactivate_users(self, request, queryset):
    updated = queryset.update(is_active=False)

    self.message_user(
      request,
      f"{updated} ta foydalanuvchi bloklandi.",
      level='warning'
    )

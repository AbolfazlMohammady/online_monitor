# سیستم صورت جلسات کمیسیون کیفیت

## بررسی کلی

این سند راهنمای پیاده‌سازی سیستم مدیریت **صورت جلسات** برای تب کمیسیون کیفیت است. سیستم امکان ایجاد، نمایش، ویرایش و حذف صورت جلسات را فراهم می‌کند.

## ساختار پیاده‌سازی

### 1. مدل (Model)

#### MeetingMinutes

فایل: [experiment/models.py](experiment/models.py#L344-L360)

```python
class MeetingMinutes(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="پروژه")
    minutes_number = models.IntegerField(verbose_name="شماره صورت جلسه")
    minutes_date = jmodels.jDateField(verbose_name="تاریخ صورت جلسه")
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
```

**ویژگی‌ها:**
- **project**: ارتباط با پروژه (ForeignKey)
- **minutes_number**: شماره صورت جلسه (عدد صحیح)
- **minutes_date**: تاریخ صورت جلسه (تقویم شمسی)
- **description**: توضیحات اضافی
- **created_at**: تاریخ و زمان ایجاد (خودکار)
- **unique_together**: ترکیب (project, minutes_number) یکتا است (تکرار شماره صورت جلسه برای پروژه غیرممکن)

### 2. فرم (Form)

فایل: [experiment/forms.py](experiment/forms.py#L380-L413)

#### MeetingMinutesForm

```python
class MeetingMinutesForm(forms.ModelForm):
    minutes_date = JalaliDateField(
        widget=AdminJalaliDateWidget,
        label='تاریخ صورت جلسه',
        required=True
    )
```

**فیلدها:**
- **project**: انتخاب پروژه (Select2 widget)
  - فیلتر شده بر اساس دسترسی کاربر (superuser - همه، سایرین - فقط پروژه‌های قابل دسترس)
- **minutes_number**: شماره صورت جلسه (NumberInput)
- **minutes_date**: تاریخ صورت جلسه (JalaliDateField با تقویم شمسی)
- **description**: توضیحات (Textarea)

### 3. Views

فایل: [experiment/views.py](experiment/views.py#L951-L1068)

#### meeting_minutes_create()

ایجاد صورت جلسه جدید

**روش درخواست:** POST (افزودن) / GET (نمایش فرم)

**تابع موردی:**
- دریافت داده‌های فرم
- ذخیره صورت جلسه
- هدایت به لیست صورت جلسات

#### meeting_minutes_list()

نمایش لیست صورت جلسات با فیلترها و صفحه‌بندی

**فیلترها:**
- **project**: فیلتر بر اساس پروژه
- **date_from**: فیلتر بر اساس تاریخ شروع
- **date_to**: فیلتر بر اساس تاریخ پایان

**مشخصات:**
- **صفحه‌بندی**: 10 مورد در هر صفحه
- **مرتب‌سازی**: نزولی بر اساس `minutes_date` سپس `created_at`
- **کنترل دسترسی**: فقط پروژه‌های قابل دسترس کاربر نمایش داده می‌شود

#### meeting_minutes_update()

ویرایش صورت جلسه موجود

**روش درخواست:** POST (بروزرسانی) / GET (نمایش فرم)

#### meeting_minutes_delete()

حذف صورت جلسه

**روش درخواست:** POST (تایید حذف)

**صفحه تایید:** `meeting_minutes_confirm_delete.html`

### 4. URLs

فایل: [experiment/urls.py](experiment/urls.py)

```python
path('meeting-minutes/', views.meeting_minutes_list, name='meeting_minutes_list'),
path('meeting-minutes/create/', views.meeting_minutes_create, name='meeting_minutes_create'),
path('meeting-minutes/<int:pk>/update/', views.meeting_minutes_update, name='meeting_minutes_update'),
path('meeting-minutes/<int:pk>/delete/', views.meeting_minutes_delete, name='meeting_minutes_delete'),
```

### 5. Templates

#### meeting_minutes_form.html

فایل: [experiment/templates/experiment/meeting_minutes_form.html](experiment/templates/experiment/meeting_minutes_form.html)

**مشخصات:**
- فرم Bootstrap-based
- تقویم شمسی برای انتخاب تاریخ
- دکمه‌های ناوبری (بازگشت، افزودن/بروزرسانی)

#### meeting_minutes_list.html

فایل: [experiment/templates/experiment/meeting_minutes_list.html](experiment/templates/experiment/meeting_minutes_list.html)

**مشخصات:**
- جدول لیست صورت جلسات
- فیلترهای انتخابی (پروژه، تاریخ شروع، تاریخ پایان)
- صفحه‌بندی (10 مورد در صفحه)
- عملیات (ویرایش، حذف)
- نمایش آمار (تعداد کل و شماره صفحه)

#### meeting_minutes_confirm_delete.html

فایل: [experiment/templates/experiment/meeting_minutes_confirm_delete.html](experiment/templates/experiment/meeting_minutes_confirm_delete.html)

**مشخصات:**
- صفحه تایید حذف
- نمایش مشخصات صورت جلسه (پروژه و شماره)
- دکمه‌های حذف و انصراف

## نحوه استفاده

### افزودن صورت جلسه جدید

1. به صفحه لیست صورت جلسات رفته و دکمه "افزودن صورت جلسه جدید" را کلیک کنید
2. URL: `/experiment/meeting-minutes/create/`
3. فرم را پر کنید:
   - **پروژه**: انتخاب پروژه (الزامی)
   - **شماره صورت جلسه**: وارد کردن شماره (الزامی)
   - **تاریخ صورت جلسه**: انتخاب تاریخ از تقویم شمسی (الزامی)
   - **توضیحات**: توضیحات اضافی (اختیاری)
4. دکمه "افزودن" را کلیک کنید

### نمایش لیست صورت جلسات

1. به صفحه: `/experiment/meeting-minutes/`
2. صورت جلسات در جدول نمایش داده می‌شوند
3. استفاده از فیلترها برای جستجو:
   - انتخاب پروژه
   - تنظیم تاریخ شروع و پایان
4. کلیک بر دکمه "جستجو"

### ویرایش صورت جلسه

1. در لیست صورت جلسات، دکمه "ویرایش" (مداد) را کلیک کنید
2. URL: `/experiment/meeting-minutes/<id>/update/`
3. فرم را تغییر داده و دکمه "بروزرسانی" را کلیک کنید

### حذف صورت جلسه

1. در لیست صورت جلسات، دکمه "حذف" (سطل زباله) را کلیک کنید
2. صفحه تایید حذف نمایش داده می‌شود
3. دکمه "حذف" را کلیک کنید تا صورت جلسه حذف شود

## بررسی و تست

### بررسی سروری

```bash
# بررسی syntax
python -m py_compile experiment/models.py
python -m py_compile experiment/forms.py
python -m py_compile experiment/views.py

# بررسی پروژه
python manage.py check

# ایجاد migrations
python manage.py makemigrations

# اعمال migrations
python manage.py migrate
```

### بررسی در مرورگر

1. صفحه ایجاد:
   - بررسی فرم و فیلدها
   - بررسی تقویم شمسی
   - ثبت و بررسی ذخیره

2. صفحه لیست:
   - بررسی نمایش صورت جلسات
   - بررسی فیلترها و جستجو
   - بررسی صفحه‌بندی

3. صفحه ویرایش:
   - تغییر داده‌ها
   - بررسی بروزرسانی

4. صفحه حذف:
   - بررسی تایید حذف
   - بررسی حذف صورت جلسات

## نکات مهم

### کنترل دسترسی

- کاربران عادی فقط صورت جلسات پروژه‌های قابل دسترس خود را می‌بینند
- Super users همه صورت جلسات را می‌بینند

### مرتب‌سازی

- صورت جلسات بر اساس **تاریخ صورت جلسه** (نزولی) مرتب می‌شوند
- اگر تاریخ مساوی باشد، بر اساس **تاریخ ایجاد** مرتب می‌شوند

### صفحه‌بندی

- هر صفحه **10 مورد** نمایش می‌دهد
- ناوبری صفحات از طریق دکمه‌های ناوبری (ابتدا، قبلی، بعدی، انتها)

### تقویم شمسی

- استفاده از `JalaliDateField` و `AdminJalaliDateWidget`
- تاریخ به صورت `YYYY/MM/DD` نمایش داده می‌شود
- تقویم خودکار هنگام کلیک روی فیلد باز می‌شود

## رفع مشکلات

### مشکل: تقویم نمایش داده نمی‌شود

**راه حل:**
- بررسی load بودن فایل‌های CSS و JS تقویم
- بررسی Console برای خطاهای JavaScript

### مشکل: فیلتر تاریخ کار نمی‌کند

**راه حل:**
- بررسی فرمت تاریخ (باید `YYYY/MM/DD` باشد)
- بررسی موجود بودن کتابخانه `jalali_date`

### مشکل: صورت جلسه ذخیره نمی‌شود

**راه حل:**
- بررسی اعتبارسنجی فرم (validation errors)
- بررسی دسترسی به پروژه
- بررسی uniqueness constraint (شماره صورت جلسه برای پروژه)

## تکامل آینده

- اضافه کردن فیلدهای اضافی (مدت جلسه، حاضرین، گیرندگان تصمیم)
- اضافه کردن فایل‌های پیوستی
- ارسال اعلان‌ها
- صادر کردن صورت جلسه به PDF

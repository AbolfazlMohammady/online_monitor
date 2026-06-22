# سیستم صورت جلسات و نتایج آزمایشات کمیسیون کیفیت

## بررسی کلی

این سند راهنمای پیاده‌سازی دو سیستم جدید برای تب کمیسیون کیفیت است:
1. **سیستم صورت جلسات**: مدیریت صورت جلسات
2. **سیستم نتایج آزمایشات**: نمایش نمودارهای تحلیلی نتایج آزمایشات

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

---

# بخش دوم: سیستم نتایج آزمایشات

## بررسی کلی

سیستم نتایج آزمایشات برای **نمایش نمودارهای تحلیلی** نتایج آزمایشات طراحی شده است. این سیستم داده‌های پاسخ‌های آزمایش را بر اساس **میانگین ماهانه** محاسبه و نمایش می‌دهد.

## ویژگی‌های اصلی

### 1. فیلترها
- **پروژه**: انتخاب پروژه خاص
- **نوع آزمایش**: انتخاب نوع آزمایش (زیرساس، عساس، خاکریزی، بتن، آسفالت)
- **بازه زمانی**: تنظیم از تاریخ و تا تاریخ

### 2. نمودارهای نمایشی
- **Control Xbar-S**: میانگین ماهانه تراکم
- **Control Xbar-R**: میانگین ماهانه مقاومت فشاری
- **هیستاگرام**: توزیع فرکانسی نتایج
- **پراکندگی**: رابطه بین نتایج مختلف پروژه‌ها

### 3. محاسبات
- **میانگین ماهانه**: برای هر ماه، تمام نتایج آزمایشات جمع شده و میانگین محاسبه می‌شود
- **شمارش**: تعداد نتایج برای هر نوع آزمایش

## View اصلی

فایل: [experiment/views.py](experiment/views.py#L1070-L1200)

### experiment_results_charts(request)

```python
@login_required
def experiment_results_charts(request):
    """نمایش نمودارهای نتایج آزمایشات"""
    # فیلترهای request
    project_id = request.GET.get('project', '')
    subtype_id = request.GET.get('subtype', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # محاسبه میانگین ماهانه
    # جمع و میانگین نتایج
```

**فرآیند محاسبه:**
1. دریافت تمام پاسخ‌های آزمایش
2. فیلتر کردن بر اساس پارامترهای request
3. تجمیع داده‌ها بر اساس ماه
4. محاسبه میانگین برای هر ماه
5. ارسال داده‌ها به template برای رسم نمودارها

## URL و دسترسی

فایل: [experiment/urls.py](experiment/urls.py)

```
/experiment/experiment-results/  →  experiment_results_charts
```

**پارامترهای GET:**
```
?project=1&subtype=2&date_from=1402/01/01&date_to=1403/12/31
```

## Template

فایل: [experiment/templates/experiment/experiment_results_charts.html](experiment/templates/experiment/experiment_results_charts.html)

**بخش‌های اصلی:**
1. **Toolbar**: دکمه‌های بازگشت و ناوبری
2. **Filter Section**: فیلترهای جستجو
3. **Statistics**: نمایش آمار کل نتایج
4. **Charts Grid**: نمایش چهار نمودار در یک شبکه 2×2

### نمودارهای JavaScript

استفاده از Chart.js برای رسم نمودارها:

#### Control Xbar-S
- نوع: Line Chart
- داده: میانگین ماهانه تراکم
- رنگ: آبی (Primary)

#### Control Xbar-R
- نوع: Line Chart
- داده: میانگین ماهانه مقاومت فشاری
- رنگ: سبز (Success)

#### هیستاگرام
- نوع: Bar Chart
- داده: تعداد نتایج تراکم و مقاومت برای هر ماه
- رنگ: چند رنگ

#### پراکندگی
- نوع: Scatter Chart
- داده: رابطه بین نتایج مختلف
- رنگ: یک رنگ برای هر پروژه

## نحوه استفاده

### دسترسی به صفحه

1. برو به: `/experiment/experiment-results/`
2. صفحه نمودارهای نتایج آزمایشات نمایش داده می‌شود

### فیلتر کردن نتایج

1. **انتخاب پروژه** (اختیاری):
   - از dropdown "پروژه" انتخاب کن
   - فقط پروژه‌های قابل دسترس نمایش داده می‌شوند

2. **انتخاب نوع آزمایش** (اختیاری):
   - از dropdown "نوع آزمایش" انتخاب کن
   - شامل تمام subtypes است

3. **تنظیم بازه زمانی** (اختیاری):
   - "از تاریخ": تاریخ شروع (تقویم شمسی)
   - "تا تاریخ": تاریخ پایان (تقویم شمسی)

4. کلیک بر دکمه "جستجو"

### خواندن نمودارها

#### Control Xbar-S (تراکم)
- محور X: ماه‌ها
- محور Y: میانگین تراکم
- نشان‌دهنده: تاثیر تاریخ بر میانگین تراکم

#### Control Xbar-R (مقاومت فشاری)
- محور X: ماه‌ها
- محور Y: میانگین مقاومت فشاری
- نشان‌دهنده: تاثیر تاریخ بر میانگین مقاومت

#### هیستاگرام
- محور X: ماه‌ها
- محور Y: تعداد نتایج
- نشان‌دهنده: تعداد آزمایشات برای هر نوع

#### پراکندگی
- محور X: نتایج تراکم
- محور Y: نتایج مقاومت فشاری
- رنگ: پروژه‌های مختلف
- نشان‌دهنده: رابطه بین دو متغیر

## بررسی و تست

### تست Functional

1. دسترسی به صفحه:
   - بررسی لود شدن صفحه
   - بررسی نمایش فیلترها

2. فیلترها:
   - انتخاب پروژه و بررسی تغییر نمودارها
   - انتخاب نوع آزمایش
   - تنظیم تاریخ و بررسی تغییر داده‌ها

3. نمودارها:
   - بررسی رسم شدن صحیح نمودارها
   - بررسی رنگ‌ها و labels
   - Hover بر نمودارها برای مشاهده داده‌ها

### تست کنترل دسترسی

- کاربر عادی: فقط پروژه‌های خود را می‌بیند
- Super user: تمام پروژه‌ها را می‌بیند

## نکات فنی

### محاسبه میانگین

```python
# برای هر ماه:
میانگین = مجموع(نتایج) / تعداد(نتایج)

# مثال:
اگر در ماه خردادماه 1402:
- 5 نتیجه تراکم: [90, 92, 91, 93, 89]
- میانگین = (90+92+91+93+89) / 5 = 91
```

### تبدیل تاریخ

- تاریخ جلالی (فارسی): YYYY/MM/DD
- تاریخ میلادی: YYYY-MM-DD
- تبدیل خودکار در view توسط `jalali_date.to_gregorian()`

### JSON Serialization

- داده‌های نمودار به صورت JSON ارسال می‌شوند
- رندر در JavaScript توسط Chart.js

## رفع مشکلات

### مشکل: نمودارها نمایش داده نمی‌شوند

**راه حل:**
- بررسی لود بودن Chart.js
- بررسی Console برای خطاهای JavaScript
- بررسی موجود بودن داده‌ها (آیا پاسخ‌های آزمایشی وجود دارند؟)

### مشکل: داده‌های نمودار خالی است

**راه حل:**
- بررسی وجود پاسخ‌های آزمایشی در database
- بررسی فیلترهای انتخاب شده
- بررسی تاریخ‌های آزمایشات

### مشکل: فیلتر تاریخ کار نمی‌کند

**راه حل:**
- فرمت تاریخ را بررسی کن (YYYY/MM/DD)
- مطمئن شو که تاریخ از < تاریخ تا است

## تکاملات آینده

1. **صادرات PDF**: خروجی نمودارها به فایل PDF
2. **صادرات Excel**: صادرات داده‌های خام
3. **اعلانات**: اطلاع‌رسانی هنگام نتایج غیرعادی
4. **مقایسه پروژه‌ها**: مقایسه سری زمانی بین پروژه‌ها
5. **پیش‌بینی**: استفاده از Machine Learning برای پیش‌بینی نتایج آینده

## ارتباط با سایر بخش‌ها

- **Models**: از `ExperimentResponse` برای دریافت نتایج استفاده می‌کند
- **Views**: مرتبط با `experiment_response_list`
- **URLs**: ثبت شده در `experiment/urls.py`
- **Templates**: استفاده از `base.html` برای layout پایه

---

## خلاصه کلی

سیستم جدید شامل:
- ✅ مدل `MeetingMinutes` برای صورت جلسات
- ✅ فرم `MeetingMinutesForm` برای ورود داده
- ✅ 4 views برای مدیریت صورت جلسات
- ✅ 3 templates برای نمایش UI
- ✅ View `experiment_results_charts` برای نتایج آزمایشات
- ✅ Template `experiment_results_charts.html` با 4 نمودار
- ✅ URLs و routing مناسب
- ✅ فیلتر و جستجو
- ✅ کنترل دسترسی کاربر

**Status**: ✅ آماده برای استفاده

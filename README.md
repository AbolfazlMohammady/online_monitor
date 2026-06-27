# نرم‌افزار پایش و مدیریت کنترل کیفیت

مسیر مستقیم در مرورگر:

/auth/experiment/experiment-results/

اگر لوکال اجرا می‌کنید:

http://127.0.0.1:8000/auth/experiment/experiment-results/

از منو هم می‌توانید بروید:

آزمایشات → نتایج آزمایشات

برای تست فیلتر، مثلاً:

/auth/experiment/experiment-results/?project=ID&layer=embankment&date_from=1402/01/01&date_to=1404/12/29

layer=embankment یعنی خاکریزی
project=ID را با id واقعی پروژه گردیان عوض کنید (از dropdown یا URL بعد از یک بار جستجو)
پاکسازی: همان دکمه «پاکسازی» در صفحه، یا باز کردن /auth/experiment/experiment-results/ بدون پارامتر.
این پروژه یک سیستم آنلاین برای مدیریت و پایش فرآیندهای کنترل کیفیت در پروژه‌ها است. هدف آن تسهیل در ثبت، نظارت و تحلیل داده‌های مرتبط با کنترل کیفیت می‌باشد.

---

## راه‌اندازی پروژه

### 1. ساخت محیط مجازی و نصب وابستگی‌ها

**الف. ساخت محیط مجازی (virtual environment):**

```sh
python -m venv venv
```

**ب. فعال‌سازی محیط مجازی:**

* در ویندوز:

```sh
venv\Scripts\activate
```

* در لینوکس/macOS:

```sh
source venv/bin/activate
```

**ج. نصب وابستگی‌ها از فایل **\`\`**:**

```sh
pip install -r requirements.txt
```

---

### 2. تنظیم فایل محیطی (`.env`)

1. نام فایل `.env-sample` را به `.env` تغییر دهید.
2. یک کلید مخفی جدید ایجاد کنید:

```sh
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. مقدار تولید شده را در فایل `.env` قرار دهید:

```
SECRET_KEY=your_generated_key
```

---

### 3. ساخت پایگاه داده

**ا. ایجاد migration‌ها**

```sh
python manage.py makemigrations
```

**ب. اعمال migrationها**

```sh
python manage.py migrate
```

---

### 4. ایجاد کاربر مدیر (اختیاری)

```sh
python manage.py createsuperuser
```

---

### 5. اجرای سرور توسعه

```sh
python manage.py runserver
```

---

## دسترسی‌ها

* پنل مدیریت: `http://localhost:8000/admin/`
* صفحات مربوط به پروژه: بر اساس ساختار URL ها

---

## مشارکت

در صورت رغبت به مشارکت در توسعه پروژه، فورک کرده، تغییرات مورد نظر را اعمال و Pull Request ارسال نمایید.

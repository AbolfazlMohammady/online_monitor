# رفع مشکل نمایش دراپ‌داون نقش تاییدکننده در فرم تایید آزمایش

## مسیرهای تغییر
- `experiment/forms.py`
- `experiment/templates/experiment/experiment_approval_form.html`
- `experiment/templates/experiment/experiment_request_approval_form.html`

## شرح تغییر
- فرم `ExperimentApprovalForm` اکنون در صورتی که فیلد `role` پنهان باشد، فقط یک ورودی مخفی (`HiddenInput`) تولید می‌کند.
- وقتی کاربر چند نقش تاییدکننده دارد، فیلد `role` به صورت یک `select` نمایش داده می‌شود (حالا از `ChoiceField` استفاده می‌شود تا گزینه‌ها درست رندر شوند).
- در قالب، بیش از یک بار `{{ form.role }}` رندر نمی‌شود و در نتیجه دراپ‌داون نامشخص اضافی بالای فرم حذف شده است.
- مشکل جدید: در فرم تایید درخواست (`ExperimentRequestApprovalForm`) فیلد `approval_date` به صورت یک ورودی متنی ساده نمایش داده می‌شد؛ اکنون این فیلد دارای کلاس `jalali_date-input` شده و در قالب `experiment_request_approval_form.html` فایل‌های CSS/JS مربوط به تقویم شمسی (persian-datepicker) بارگذاری و مقداردهی می‌شوند تا کاربر با کلیک روی فیلد، تاریخ را از تقویم انتخاب کند.

## مسیر دقیق تغییرات برای تست
- [experiment/forms.py](experiment/forms.py#L162-L170): اضافه شدن `approval_date` widget attrs برای کلاس `jalali_date-input`.
- [experiment/templates/experiment/experiment_request_approval_form.html](experiment/templates/experiment/experiment_request_approval_form.html#L1-L80): بارگذاری `form.media` و `persian-datepicker` و اضافه شدن اسکریپت مقداردهی تقویم.
- [experiment/templates/experiment/experiment_approval_form.html](experiment/templates/experiment/experiment_approval_form.html#L1-L60): (تذکر) همین قالب قبلاً تقویم را مقداردهی می‌کرد.

## روش تست
1. چه در حالت ایجاد تاییدیه پاسخ (`experiment/experiment-approval/create/<response_id>/`) و چه در تایید درخواست (`experiment/requests/<request_id>/approval/`):
   - صفحه را باز کنید و مطمئن شوید فیلد تاریخ به صورت ورودی تاریخ با تقویم شمسی بازشونده نمایش داده می‌شود.
   - روی فیلد کلیک کنید، تقویم باز شود و تاریخ انتخاب شود.
2. برای بررسی سروری (در صورت نیاز):

```bash
python manage.py shell
from experiment.models import ExperimentResponse, ExperimentRequest
# بررسی approvers برای response
resp = ExperimentResponse.objects.get(pk=42)
print(resp.get_required_approval_roles())
for role in resp.get_required_approval_roles():
    print(role, [u.username for u in resp.get_approvers_for_role(role)])
```

## تست کد
- `python -m py_compile experiment/forms.py`
- بعد از نصب وابستگی‌ها برای بررسی کامل پروژه:
  - `python manage.py check`

## نکته
اگر با `python manage.py check` به مشکل `ModuleNotFoundError: No module named 'grappelli'` برخوردید، ابتدا مطمئن شوید که بسته‌های مورد نیاز در محیط فعال نصب شده‌اند.

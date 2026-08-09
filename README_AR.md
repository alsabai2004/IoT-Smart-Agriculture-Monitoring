# دليل تشغيل مشروع Smart Agriculture Monitoring

## محتويات التسليم
- `Source_Code/publisher.py` - توليد قراءات حساسات افتراضية وإرسالها عبر MQTT.
- `Source_Code/gateway.py` - استقبال البيانات الخام، التحقق من JSON، إضافة timestamp، تطبيق منطق التنبيه، ثم النشر إلى topic جديد.
- `Source_Code/subscriber.py` - عرض البيانات المعالجة والتنبيهات بشكل لحظي.
- `Source_Code/requirements.txt` - المكتبة المطلوبة للتشغيل.
- `Report/IoT_Smart_Agriculture_Report.docx` - تقرير قابل للتعديل.
- `Report/IoT_Smart_Agriculture_Report.pdf` - نسخة PDF للتسليم.
- `Presentation/IoT_Smart_Agriculture_Presentation.pptx` - عرض قابل للتعديل.
- `Screenshots/` - صور توضيحية جاهزة، ويمكن استبدالها بلقطات تشغيل حقيقية.
- `Assets/architecture_diagram.svg` - مخطط النظام قابل للتعديل.

## قبل التشغيل
1. افتح مجلد `Source_Code`.
2. ثبّت المكتبات:

```bash
pip install -r requirements.txt
```

## يفضّل تعديل GroupX قبل التسليم
غيّر `groupX` في أسماء الـ topics إلى رقم مجموعتك الحقيقي داخل الملفات الثلاثة، مثلًا:

```text
iot/project/group7/agriculture/raw
iot/project/group7/agriculture/processed
```

## طريقة التشغيل في 3 نوافذ Terminal
### النافذة الأولى - Gateway
```bash
python gateway.py
```

### النافذة الثانية - Subscriber
```bash
python subscriber.py
```

### النافذة الثالثة - Publisher
```bash
python publisher.py
```

## ماذا تتوقع أن ترى؟
- الـ Publisher يرسل JSON كل 2-3 ثوانٍ.
- الـ Gateway يتحقق من JSON ويضيف timestamp ويحدد الحالة.
- الـ Subscriber يطبع `NORMAL` أو `WARNING` أو `ALERT` حسب القيم.

## قواعد التنبيه المستخدمة
- درجة الحرارة `>= 32` مئوية -> `ALERT`
- الرطوبة `>= 80%` -> `ALERT`
- درجة الحرارة `>= 29` أو الرطوبة `<= 35%` -> `WARNING`
- غير ذلك -> `NORMAL`

## لقطات الشاشة المطلوبة للتقرير
بعد التشغيل الفعلي، خذ صورًا لـ:
1. Publisher أثناء الإرسال.
2. رسائل MQTT/مخرجات Gateway.
3. Subscriber أثناء العرض اللحظي.
4. حالة Alert واضحة.

يمكنك استبدال الصور الموجودة في `Screenshots/` بهذه الصور الحقيقية ثم تحديثها داخل التقرير إذا رغبت.

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True)),
                ("price_rub", models.PositiveIntegerField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Курс",
                "verbose_name_plural": "Курсы",
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("telegram_id", models.BigIntegerField(unique=True, verbose_name="Telegram ID")),
                ("username", models.CharField(blank=True, max_length=64)),
                ("full_name", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("is_blocked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Лид",
                "verbose_name_plural": "Лиды",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="PromptTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("system_prompt", models.TextField()),
                ("is_active", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Шаблон промпта",
                "verbose_name_plural": "Шаблоны промптов",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="OperatorActionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("level", models.CharField(choices=[("info", "Info"), ("warning", "Warning"), ("error", "Error")], default="info", max_length=16)),
                ("action_type", models.CharField(max_length=64)),
                ("entity", models.CharField(max_length=64)),
                ("entity_id", models.CharField(blank=True, max_length=64)),
                ("actor", models.CharField(blank=True, max_length=128)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Действие оператора",
                "verbose_name_plural": "Журнал действий операторов",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="EnrollmentRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("new", "New"), ("consulting", "Consulting"), ("waiting_payment", "Waiting payment"), ("paid", "Paid"), ("cancelled", "Cancelled")], default="new", max_length=32)),
                ("priority", models.BooleanField(default=False)),
                ("source", models.CharField(default="telegram", max_length=64)),
                ("operator_note", models.TextField(blank=True)),
                ("last_contact_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="enrollment_requests", to="botmanager.course")),
                ("lead", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="enrollment_requests", to="botmanager.lead")),
            ],
            options={
                "verbose_name": "Заявка на курс",
                "verbose_name_plural": "Заявки на курсы",
                "ordering": ("-updated_at",),
            },
        ),
        migrations.AddField(
            model_name="lead",
            name="preferred_course",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="interested_leads", to="botmanager.course"),
        ),
        migrations.CreateModel(
            name="ConsultationDialog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("open", "Open"), ("waiting_client", "Waiting client"), ("closed", "Closed")], default="open", max_length=32)),
                ("summary", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("enrollment_request", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="consultations", to="botmanager.enrollmentrequest")),
                ("lead", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="consultations", to="botmanager.lead")),
            ],
            options={
                "verbose_name": "Консультация",
                "verbose_name_plural": "Консультации",
                "ordering": ("-updated_at",),
            },
        ),
        migrations.CreateModel(
            name="DialogMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sender_type", models.CharField(choices=[("client", "Client"), ("bot", "Bot"), ("operator", "Operator")], max_length=16)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("consultation", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="messages", to="botmanager.consultationdialog")),
            ],
            options={
                "verbose_name": "Сообщение консультации",
                "verbose_name_plural": "Сообщения консультации",
                "ordering": ("created_at",),
            },
        ),
    ]

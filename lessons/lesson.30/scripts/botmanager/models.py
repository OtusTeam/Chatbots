from __future__ import annotations

from django.db import models


class EnrollmentStatus(models.TextChoices):
    NEW = "new", "New"
    CONSULTING = "consulting", "Consulting"
    WAITING_PAYMENT = "waiting_payment", "Waiting payment"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"


class ConsultationStatus(models.TextChoices):
    OPEN = "open", "Open"
    WAITING_CLIENT = "waiting_client", "Waiting client"
    CLOSED = "closed", "Closed"


class SenderType(models.TextChoices):
    CLIENT = "client", "Client"
    BOT = "bot", "Bot"
    OPERATOR = "operator", "Operator"


class ActionLevel(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    ERROR = "error", "Error"


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price_rub = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self) -> str:
        return self.title


class Lead(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=64, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    preferred_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interested_leads",
    )
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Лид"
        verbose_name_plural = "Лиды"

    def __str__(self) -> str:
        return self.full_name


class EnrollmentRequest(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="enrollment_requests")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="enrollment_requests")
    status = models.CharField(max_length=32, choices=EnrollmentStatus.choices, default=EnrollmentStatus.NEW)
    priority = models.BooleanField(default=False)
    source = models.CharField(max_length=64, default="telegram")
    operator_note = models.TextField(blank=True)
    last_contact_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Заявка на курс"
        verbose_name_plural = "Заявки на курсы"

    def __str__(self) -> str:
        return f"{self.lead.full_name} -> {self.course.title}"


class ConsultationDialog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="consultations")
    enrollment_request = models.ForeignKey(
        EnrollmentRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations",
    )
    status = models.CharField(max_length=32, choices=ConsultationStatus.choices, default=ConsultationStatus.OPEN)
    summary = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Консультация"
        verbose_name_plural = "Консультации"

    def __str__(self) -> str:
        return f"Consultation #{self.pk} ({self.lead.full_name})"


class DialogMessage(models.Model):
    consultation = models.ForeignKey(ConsultationDialog, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=16, choices=SenderType.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Сообщение консультации"
        verbose_name_plural = "Сообщения консультации"

    def __str__(self) -> str:
        return f"{self.sender_type}: {self.message[:40]}"


class PromptTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Шаблон промпта"
        verbose_name_plural = "Шаблоны промптов"

    def __str__(self) -> str:
        return self.name


class OperatorActionLog(models.Model):
    level = models.CharField(max_length=16, choices=ActionLevel.choices, default=ActionLevel.INFO)
    action_type = models.CharField(max_length=64)
    entity = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64, blank=True)
    actor = models.CharField(max_length=128, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Действие оператора"
        verbose_name_plural = "Журнал действий операторов"

    def __str__(self) -> str:
        return f"{self.action_type}: {self.message[:40]}"

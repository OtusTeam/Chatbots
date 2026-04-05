from __future__ import annotations

import csv
import io
from typing import Any
from django.utils import timezone

from .models import (
    ConsultationDialog,
    ConsultationStatus,
    Course,
    DialogMessage,
    EnrollmentRequest,
    EnrollmentStatus,
    Lead,
    OperatorActionLog,
    PromptTemplate,
    SenderType,
)


def get_active_prompt() -> PromptTemplate | None:
    return PromptTemplate.objects.filter(is_active=True).order_by("name").first()


def get_active_prompt_name() -> str:
    prompt = get_active_prompt()
    return prompt.name if prompt else "не выбран"


def log_operator_action(
    action_type: str,
    entity: str,
    entity_id: str = "",
    actor: str = "system",
    message: str = "",
) -> None:
    OperatorActionLog.objects.create(
        action_type=action_type,
        entity=entity,
        entity_id=entity_id,
        actor=actor,
        message=message,
    )


def collect_metrics() -> dict[str, int | str]:
    today = timezone.localdate()
    return {
        "new_leads_today": Lead.objects.filter(created_at__date=today).count(),
        "open_consultations": ConsultationDialog.objects.filter(status=ConsultationStatus.OPEN).count(),
        "waiting_payment_orders": EnrollmentRequest.objects.filter(status=EnrollmentStatus.WAITING_PAYMENT).count(),
        "paid_orders": EnrollmentRequest.objects.filter(status=EnrollmentStatus.PAID).count(),
        "operator_actions": OperatorActionLog.objects.count(),
        "active_prompts": PromptTemplate.objects.filter(is_active=True).count(),
    }


def recent_orders_for_lead(lead: Lead, limit: int = 5) -> list[EnrollmentRequest]:
    return list(
        lead.enrollment_requests.select_related("course").order_by("-created_at")[:limit]
    )


def get_status_label(status: str) -> str:
    mapping = {
        EnrollmentStatus.NEW: "новая",
        EnrollmentStatus.CONSULTING: "консультация",
        EnrollmentStatus.WAITING_PAYMENT: "ожидает оплату",
        EnrollmentStatus.PAID: "оплачена",
        EnrollmentStatus.CANCELLED: "отменена",
    }
    return mapping.get(status, status)


def get_metrics_for_display() -> list[tuple[str, int]]:
    metrics = collect_metrics()
    labels = {
        "new_leads_today": "Новых лидов за сегодня",
        "open_consultations": "Открытых консультаций",
        "waiting_payment_orders": "Заявок в ожидании оплаты",
        "paid_orders": "Оплаченных заявок",
        "operator_actions": "Действий операторов",
        "active_prompts": "Активных промптов",
    }
    return [(labels[key], int(metrics[key])) for key in labels]


def build_leads_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["lead_id", "telegram_id", "full_name", "username", "phone", "preferred_course", "is_blocked"])
    for lead in Lead.objects.select_related("preferred_course").order_by("created_at"):
        writer.writerow(
            [
                lead.pk,
                lead.telegram_id,
                lead.full_name,
                lead.username,
                lead.phone,
                lead.preferred_course.title if lead.preferred_course else "",
                lead.is_blocked,
            ]
        )
    return output.getvalue()


def build_orders_csv() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order_id", "lead", "course", "status", "priority", "last_contact_at", "created_at"])
    for order in EnrollmentRequest.objects.select_related("lead", "course").order_by("-created_at"):
        writer.writerow(
            [
                order.pk,
                order.lead.full_name,
                order.course.title,
                order.status,
                order.priority,
                order.last_contact_at.isoformat() if order.last_contact_at else "",
                order.created_at.isoformat(),
            ]
        )
    return output.getvalue()


def get_or_create_lead(telegram_id: int, username: str, full_name: str) -> Lead:
    lead, created = Lead.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"username": username, "full_name": full_name},
    )
    if not created:
        changed = False
        if username and lead.username != username:
            lead.username = username
            changed = True
        if full_name and lead.full_name != full_name:
            lead.full_name = full_name
            changed = True
        if changed:
            lead.save(update_fields=["username", "full_name"])
    return lead


def get_or_create_open_consultation(lead: Lead, enrollment_request: EnrollmentRequest | None = None) -> ConsultationDialog:
    consultation = ConsultationDialog.objects.filter(lead=lead, status=ConsultationStatus.OPEN).order_by("-created_at").first()
    if consultation:
        return consultation
    return ConsultationDialog.objects.create(
        lead=lead,
        enrollment_request=enrollment_request,
        summary="Диалог по выбору курса",
    )


def append_consultation_message(consultation: ConsultationDialog, sender: str, message: str) -> DialogMessage:
    msg = DialogMessage.objects.create(
        consultation=consultation,
        sender_type=sender,
        message=message.strip(),
    )
    consultation.updated_at = timezone.now()
    consultation.save(update_fields=["updated_at"])
    return msg


def list_active_courses() -> list[Course]:
    return list(Course.objects.filter(is_active=True).order_by("title"))


def find_course_by_id(course_id: int) -> Course | None:
    return Course.objects.filter(pk=course_id, is_active=True).first()


def create_enrollment_request(lead: Lead, course: Course, actor: str = "telegram-bot") -> EnrollmentRequest:
    order = EnrollmentRequest.objects.create(
        lead=lead,
        course=course,
        status=EnrollmentStatus.NEW,
        source="telegram",
        last_contact_at=timezone.now(),
    )
    log_operator_action(
        action_type="order_created",
        entity="EnrollmentRequest",
        entity_id=str(order.pk),
        actor=actor,
        message=f"Создана заявка для {lead.full_name} ({course.title}).",
    )
    return order


def touch_order_status(order: EnrollmentRequest, status: str, actor: str, note: str = "") -> EnrollmentRequest:
    order.status = status
    order.last_contact_at = timezone.now()
    if note:
        order.operator_note = note
    order.save(update_fields=["status", "last_contact_at", "operator_note", "updated_at"])
    log_operator_action(
        action_type="order_status_changed",
        entity="EnrollmentRequest",
        entity_id=str(order.pk),
        actor=actor,
        message=f"Статус заявки изменен на {get_status_label(status)}. {note}".strip(),
    )
    return order


def activate_prompt(prompt: PromptTemplate, actor: str = "operator") -> None:
    PromptTemplate.objects.update(is_active=False)
    prompt.is_active = True
    prompt.save(update_fields=["is_active", "updated_at"])
    log_operator_action(
        action_type="prompt_activated",
        entity="PromptTemplate",
        entity_id=str(prompt.pk),
        actor=actor,
        message=f"Active prompt changed to {prompt.name}.",
    )


def bootstrap_demo_data() -> dict[str, Any]:
    python_course, _ = Course.objects.get_or_create(
        slug="python-zero-to-job",
        defaults={"title": "Python: от нуля до работы", "price_rub": 39900},
    )
    ai_course, _ = Course.objects.get_or_create(
        slug="ai-bots-practice",
        defaults={"title": "Практика AI-ботов для бизнеса", "price_rub": 45900},
    )
    sales_course, _ = Course.objects.get_or_create(
        slug="sales-automation",
        defaults={"title": "Автоматизация продаж и CRM-процессы", "price_rub": 29900},
    )

    leads_seed = [
        {"telegram_id": 10001, "full_name": "Анна Петрова", "username": "anna", "preferred_course": python_course},
        {"telegram_id": 10002, "full_name": "Игорь Смирнов", "username": "igor", "preferred_course": ai_course},
        {"telegram_id": 10003, "full_name": "Мария Кузнецова", "username": "maria", "preferred_course": sales_course},
    ]
    for payload in leads_seed:
        Lead.objects.get_or_create(
            telegram_id=payload["telegram_id"],
            defaults={
                "full_name": payload["full_name"],
                "username": payload["username"],
                "preferred_course": payload["preferred_course"],
            },
        )

    anna = Lead.objects.get(telegram_id=10001)
    igor = Lead.objects.get(telegram_id=10002)

    order_anna, _ = EnrollmentRequest.objects.get_or_create(
        lead=anna,
        course=python_course,
        defaults={
            "status": EnrollmentStatus.CONSULTING,
            "priority": True,
            "source": "telegram",
            "operator_note": "Нужна консультация по расписанию и рассрочке.",
            "last_contact_at": timezone.now(),
        },
    )
    EnrollmentRequest.objects.get_or_create(
        lead=igor,
        course=ai_course,
        defaults={
            "status": EnrollmentStatus.WAITING_PAYMENT,
            "priority": False,
            "source": "telegram",
            "operator_note": "Выслана ссылка на оплату.",
            "last_contact_at": timezone.now(),
        },
    )

    consult_anna = get_or_create_open_consultation(anna, order_anna)
    if not consult_anna.messages.exists():
        append_consultation_message(consult_anna, SenderType.CLIENT, "Здравствуйте, хочу разобраться по программе Python.")
        append_consultation_message(consult_anna, SenderType.OPERATOR, "Добрый день! Подскажите, какой у вас текущий уровень?")

    prompt_default, _ = PromptTemplate.objects.get_or_create(
        name="course-consult-default",
        defaults={
            "system_prompt": "Отвечай как менеджер учебного центра: уточняй цель, предлагай подходящий курс и следующий шаг.",
            "is_active": True,
        },
    )
    PromptTemplate.objects.get_or_create(
        name="course-consult-short",
        defaults={
            "system_prompt": "Коротко отвечай по сути и всегда приглашай на консультацию с оператором.",
            "is_active": False,
        },
    )

    if PromptTemplate.objects.filter(is_active=True).count() == 0:
        activate_prompt(prompt_default, actor="seed")

    log_operator_action(
        action_type="demo_seeded",
        entity="system",
        actor="management-command",
        message="Demo data for course enrollment bot loaded.",
    )

    return {
        "courses_total": Course.objects.count(),
        "leads_total": Lead.objects.count(),
        "orders_total": EnrollmentRequest.objects.count(),
    }

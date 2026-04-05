from __future__ import annotations

from django.contrib import admin, messages
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
)
from .services import activate_prompt, log_operator_action, touch_order_status

admin.site.site_header = "Lesson 30 Admin"
admin.site.site_title = "Bot Admin"
admin.site.index_title = "Управление ботом заказов курсов"


class DialogMessageInline(admin.TabularInline):
    model = DialogMessage
    extra = 0
    readonly_fields = ("sender_type", "message", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "price_rub", "is_active", "created_at")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "full_name", "username", "phone", "preferred_course", "is_blocked", "created_at")
    search_fields = ("telegram_id", "username", "full_name", "phone")
    list_filter = ("is_blocked", "preferred_course", "created_at")
    autocomplete_fields = ("preferred_course",)
    readonly_fields = ("created_at",)


@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ("lead", "course", "status", "priority", "last_contact_at", "updated_at")
    search_fields = ("lead__full_name", "lead__username", "lead__phone", "course__title")
    list_filter = ("status", "priority", "course", "updated_at")
    autocomplete_fields = ("lead", "course")
    readonly_fields = ("created_at", "updated_at", "last_contact_at")
    actions = (
        "set_consulting",
        "set_waiting_payment",
        "set_paid",
        "set_cancelled",
        "mark_as_priority",
    )

    def _apply_status_action(self, request, queryset, status: str, done_message: str):
        for order in queryset:
            touch_order_status(order, status, actor=request.user.username or "admin")
        self.message_user(request, done_message.format(count=queryset.count()))

    @admin.action(description="Перевести в консультацию")
    def set_consulting(self, request, queryset):
        self._apply_status_action(
            request,
            queryset,
            EnrollmentStatus.CONSULTING,
            "Переведено в консультацию: {count}",
        )

    @admin.action(description="Перевести в ожидание оплаты")
    def set_waiting_payment(self, request, queryset):
        self._apply_status_action(
            request,
            queryset,
            EnrollmentStatus.WAITING_PAYMENT,
            "Переведено в ожидание оплаты: {count}",
        )

    @admin.action(description="Перевести в оплачено")
    def set_paid(self, request, queryset):
        self._apply_status_action(
            request,
            queryset,
            EnrollmentStatus.PAID,
            "Переведено в оплачено: {count}",
        )

    @admin.action(description="Перевести в отменено")
    def set_cancelled(self, request, queryset):
        self._apply_status_action(
            request,
            queryset,
            EnrollmentStatus.CANCELLED,
            "Переведено в отменено: {count}",
        )

    @admin.action(description="Пометить как приоритетные")
    def mark_as_priority(self, request, queryset):
        updated = queryset.update(priority=True, updated_at=timezone.now())
        for order in queryset:
            log_operator_action(
                action_type="priority_marked",
                entity="EnrollmentRequest",
                entity_id=str(order.pk),
                actor=request.user.username or "admin",
                message="Заявка помечена как приоритетная.",
            )
        self.message_user(request, f"Приоритетных заявок: {updated}")


@admin.register(ConsultationDialog)
class ConsultationDialogAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "enrollment_request", "status", "updated_at")
    search_fields = ("lead__full_name", "lead__username", "summary")
    list_filter = ("status", "updated_at")
    autocomplete_fields = ("lead", "enrollment_request")
    readonly_fields = ("created_at", "updated_at")
    inlines = (DialogMessageInline,)
    actions = ("close_consultations",)

    @admin.action(description="Закрыть выбранные консультации")
    def close_consultations(self, request, queryset):
        updated = queryset.update(status=ConsultationStatus.CLOSED, updated_at=timezone.now())
        for consultation in queryset:
            log_operator_action(
                action_type="consultation_closed",
                entity="ConsultationDialog",
                entity_id=str(consultation.pk),
                actor=request.user.username or "admin",
                message="Консультация закрыта из админки.",
            )
        self.message_user(request, f"Закрыто консультаций: {updated}")


@admin.register(DialogMessage)
class DialogMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "consultation", "sender_type", "short_message")
    search_fields = ("consultation__lead__full_name", "message")
    list_filter = ("sender_type", "created_at")
    autocomplete_fields = ("consultation",)
    readonly_fields = ("consultation", "sender_type", "message", "created_at")

    def short_message(self, obj):
        return obj.message[:80]


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    search_fields = ("name", "system_prompt")
    list_filter = ("is_active", "updated_at")
    readonly_fields = ("updated_at",)
    actions = ("activate_selected_prompt",)

    @admin.action(description="Сделать выбранный шаблон активным")
    def activate_selected_prompt(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Выберите ровно один шаблон, который должен стать активным.",
                level=messages.ERROR,
            )
            return

        selected_prompt = queryset.first()
        if selected_prompt is not None:
            activate_prompt(selected_prompt, actor=request.user.username or "admin")
            self.message_user(request, f"Активный шаблон: {selected_prompt.name}")


@admin.register(OperatorActionLog)
class OperatorActionLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "level", "action_type", "entity", "entity_id", "actor", "message")
    search_fields = ("action_type", "entity", "entity_id", "actor", "message")
    list_filter = ("level", "action_type", "entity", "created_at")
    readonly_fields = ("level", "action_type", "entity", "entity_id", "actor", "message", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

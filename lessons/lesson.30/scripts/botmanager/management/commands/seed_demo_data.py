from __future__ import annotations

from django.core.management.base import BaseCommand

from botmanager.services import bootstrap_demo_data


class Command(BaseCommand):
    help = "Fill the lesson project with demo bot data."

    def handle(self, *args, **options):
        stats = bootstrap_demo_data()
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data loaded: "
                f"courses={stats['courses_total']}, "
                f"leads={stats['leads_total']}, "
                f"orders={stats['orders_total']}"
            )
        )

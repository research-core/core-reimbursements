from django.contrib import admin

from .models import Expense
from .models import Reimbursement


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    min_num = 1


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):

    list_display = ["requester_name", "total", "created", "status"]

    list_filter = ["status", "created", "modified"]

    search_fields = ["person__full_name", "ext_person_name"]

    list_select_related = ["project"]

    autocomplete_fields = ["project"]

    fields = ["person", "ext_person_name", "iban", "project"]

    readonly_fields = ["status_changed"]

    inlines = [ExpenseInline]

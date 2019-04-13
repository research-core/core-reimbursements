from django.db import models
from model_utils import Choices
from django.conf import settings
from django.shortcuts import render
from django.utils.html import format_html
from django_weasyprint import WeasyTemplateView
from localflavor.generic.models import IBANField
from django.core.exceptions import ValidationError
from model_utils.models import StatusModel, TimeStampedModel
from .reimbursement_queryset import ReimbursementQuerySet

class Reimbursement(StatusModel, TimeStampedModel):

    STATUS = Choices(
        ("0", "Pending"),
        ("P", "Printed"),
        ("S", "Submitted"),
        ("A", "Approved"),
        ("R", "Rejected"),
    )

    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    person     = models.ForeignKey(to="humanresources.Person", on_delete=models.CASCADE, blank=True, null=True)
    project    = models.ForeignKey(to="supplier.FinanceProject", on_delete=models.CASCADE, blank=True, null=True)
    iban       = IBANField(verbose_name="IBAN", blank=True, include_countries=("PT",))

    objects = ReimbursementQuerySet.as_manager()

    class Meta:
        ordering = ("-created",)
        permissions = (
            ("can_approve_reimbursements", "Approve or reject reimbursements"),
        )
        verbose_name = 'Reimbursement'
        verbose_name_plural = 'Reimbursements'

    def __str__(self):
        return f"Reimbursement for {self.requester_name}"

    def clean(self):
        if self.created_by is None:
            raise ValidationError("This proposal has no person responsible")

    # Custom methods
    # =========================================================================

    @property
    def requester_name(self):
        return self.person.full_name

    @property
    def requester_iban(self):
        return "".join(d + " " if (i + 1) % 4 == 0 else d for i, d in enumerate(self.iban))

    @property
    def total(self):
        try:
            return sum(expense.value for expense in self.expenses.all())
        except TypeError:
            # can not add Money with different currencies
            return None

    def get_project_code(self):
        if self.project:
            return self.project.financeproject_code
        else:
            return ""

    get_project_code.short_description = "project"

    def get_requisitions_status(self):
        total_expenses = self.expenses.count()
        with_req_num = self.expenses.filter(requisition_number__isnull=False).count()

        if total_expenses > 0 and total_expenses == with_req_num:
            icon = '<i class="green check icon"></i>'
        else:
            icon = '<i class="red times icon"></i>'

        return f"{icon} ({with_req_num}/{total_expenses})"

    get_requisitions_status.short_description = "requisitions"

    def status_icon(self):
        d = {
            "0": '<i class="grey clock icon"></i>',
            "P": '<i class="blue print icon"></i>',
            "S": '<i class="black lock icon"></i>',
            "A": '<i class="green thumbs up icon"></i>',
            "R": '<i class="red thumbs down icon"></i>',
        }

        icon = d.get(self.status, "")
        return format_html(f'<div align="center">{icon}</div>')

    status_icon.short_description = "status"

    def generate_pdf_view(self, request=None):
        """Returns a PDF view for this proposal."""

        template = "pdfs/reimbursement_form_pdf_template.html"

        context = {
            "reimbursement": self,
            "logo": settings.REIMBURSEMENTS_LOGO,
            # # FIXME test only
            # 'motive': 'New Hire',
            # 'proposal_date': self.contractproposal_createdon.strftime('%b %d, %Y'),
        }

        # FIXME this should be the debug, erase the `not`
        if "debug" not in request.GET:
            return render(request, template_name=template, context=context)

        return WeasyTemplateView.as_view(template_name=template, extra_context=context)(
            request
        )

import textwrap

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import render
from django.utils.html import format_html

from django_weasyprint import WeasyTemplateView
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from localflavor.generic.models import IBANField
from model_utils.models import StatusModel, TimeStampedModel
from model_utils import Choices


class Reimbursement(StatusModel, TimeStampedModel):

    STATUS = Choices(
        ("pending", "Pending"),
        ("printed", "Printed"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    person = models.ForeignKey(
        to="humanresources.Person", on_delete=models.CASCADE, blank=True, null=True
    )

    # cost_center = models.ForeignKey(
    #     to="supplier.FinanceCostCenter", on_delete=models.CASCADE, blank=True, null=True
    # )

    project = models.ForeignKey(
        to="supplier.FinanceProject", on_delete=models.CASCADE, blank=True, null=True
    )

    ext_person_name = models.CharField(max_length=80, verbose_name="Name", blank=True)
    ext_person_iban = IBANField(
        verbose_name="IBAN", blank=True, include_countries=("PT",)
    )

    class Meta:
        ordering = ("-created",)
        permissions = (
            ("can_request_for_other", "Request on behalf of someone else "),
            ("can_print", "Print Reimbursement"),
            ("can_approve", "Approve or reject Reimbursements"),
        )

    def __str__(self):
        return f"Reimbursement for {self.requester_name}"

    def clean(self):

        print(self.person, self.ext_person_name, self.ext_person_iban)

        if not self.person and not (self.ext_person_name or self.ext_person_iban):
            raise ValidationError(
                "Select a Person from the list or fill the Name and IBAN below."
            )

        elif not self.person and not (self.ext_person_name and self.ext_person_iban):
            for field_name in ("ext_person_name", "ext_person_iban"):
                if not getattr(self, field_name):
                    raise ValidationError({field_name: "This field is required."})

        # elif not self.person:

        #     # errors["person"] = "Select a Person from the list or fill in the fields below"

        #     # for field_name in ("ext_person_name", "ext_person_iban"):

        #     if not self.ext_person_name:
        #         errors["ext_person_name"] = "This field is required when no Person is selected"
        #     if not self.ext_person_iban:
        #         errors["ext_person_iban"] = "This field is required when no Person is selected"
        elif self.person:
            # TODO validate IBAN
            try:
                if not self.person.privateinfo.iban:
                    raise ValidationError(
                        "Invalid IBAN found, please complete your profile to continue."
                    )
            except Reimbursement.person.field.related_model.privateinfo.related.related_model.DoesNotExist:
                # PrivateInfo relation does not exist
                raise ValidationError(
                    "IBAN not found, please complete your profile to continue."
                )
        else:
            pass

        # if self.expenses.count() < 1:
        #     errors[NON_FIELD_ERRORS].append("At least one Expense is required")

    def save(self):
        if self.created_by is None:
            raise ValidationError("This proposal has no person responsible")
        super().save()

    # Custom methods
    # =========================================================================

    @property
    def requester_name(self):
        if self.person is not None:
            return self.person.full_name
        else:
            return self.ext_person_name

    @property
    def requester_iban(self):
        if self.person is not None:
            iban = self.person.privateinfo.iban
        else:
            iban = self.ext_person_iban

        return "".join(d + " " if (i + 1) % 4 == 0 else d for i, d in enumerate(iban))

    @property
    def total(self):
        try:
            return sum(expense.value for expense in self.expenses.all())
        except TypeError:
            # can not add Money with different currencies
            return None

    def get_project_code(self):
        if self.project:
            return self.project.abbrv
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
            "pending": '<i class="grey clock icon"></i>',
            "printed": '<i class="blue print icon"></i>',
            "submitted": '<i class="black lock icon"></i>',
            "approved": '<i class="green thumbs up icon"></i>',
            "rejected": '<i class="red thumbs down icon"></i>',
        }

        icon = d.get(self.status, "")
        return format_html(f'<div align="center">{icon}</div>')

    status_icon.short_description = "status"

    def generate_pdf_view(self, request=None):
        """Returns a PDF view for this proposal."""

        template = "pdfs/reimbursement_form_pdf_template.html"

        context = {
            "reimbursement": self,
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


class Expense(models.Model):
    """Expense to be reimbursed."""

    # TODO add attachments

    requisition_number = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    value = MoneyField(
        max_digits=11,
        decimal_places=2,
        default_currency="EUR",
        validators=[MinMoneyValidator(Money(0.01))],
    )
    reimbursement = models.ForeignKey(
        to="Reimbursement", on_delete=models.CASCADE, related_name="expenses"
    )

    def clean(self):
        self.description = self.description.strip("\n")

        # restrict number of lines
        new_lines = len(self.description.split("\n"))
        if new_lines > 8 or len(self.description) > 600:
            raise ValidationError({"description": "Too much text."})

    def short_description(self):
        return textwrap.shorten(self.description, width=100, placeholder="...")

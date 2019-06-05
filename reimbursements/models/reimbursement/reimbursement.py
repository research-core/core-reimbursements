from common.models import Permissions
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
from notifications.tools import notify

class Reimbursement(StatusModel, TimeStampedModel):

    STATUS = Choices(
        ("draft",     "Draft"),
        ("pending",   "Pending"),
        ("printed",   "Printed"),
        ("submitted", "Submitted"),
        ("approved",  "Approved"),
        ("rejected",  "Rejected"),
        ("closed",    "Closed"),
    )

    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    person = models.ForeignKey(to="humanresources.Person", on_delete=models.CASCADE, blank=True, null=True)
    iban = IBANField(verbose_name="IBAN", blank=True, include_countries=("PT",))
    order = models.ForeignKey('supplier.Order', on_delete=models.CASCADE, null=True, blank=True)

    objects = ReimbursementQuerySet.as_manager()

    class Meta:
        ordering = ("-created",)
        permissions = (
            ("manage_reimbursements", "Submit reimbursements for approval"),
            ("can_approve_reimbursements", "Approve or reject reimbursements"),
            ("receive_approved_notifications", "Receive notifications about the approved reimbursements"),
        )
        verbose_name = 'Reimbursement'
        verbose_name_plural = 'Reimbursements'

    def __str__(self):
        return f"Reimbursement for {self.person}"

    def clean(self):
        if self.created_by is None:
            raise ValidationError("This proposal has no person responsible")

    # Custom methods
    # =========================================================================

    def has_approve_permissions(self, user):
        if self.pk is None or self.status=='draft':
            return False

        perms = Permissions.objects.filter_by_auth_permissions(
            Reimbursement, ['can_approve_reimbursements']
        )

        for p in perms:
            if p.researchgroup is None and user in p.djangogroup.user_set.all():
                return True

        # get all django groups associated to the expenses
        exp_djangogroups = [e.expensecode.financeproject.costcenter.group for e in self.expenses.all()]
        # get all the research groups associated to the expenses
        exp_researchgrps = [g.group_django.first() for g in exp_djangogroups if g.group_django.first() is not None]

        # check if the user has permissions to all the expense codes research groups
        perms = perms.filter(researchgroup__in=exp_researchgrps).distinct()
        has_access = perms.count()>0
        for p in perms:
            if user not in p.djangogroup.user_set.all():
                has_access = False
                break

        return has_access

    def submit(self):
        if self.expenses.count() <= 0:
            raise Exception("Add at least one Expense to be reimbursed.")

        self.status = 'pending'
        self.save()

        perms = Permissions.objects.filter_by_auth_permissions(
            Reimbursement, ['can_approve_reimbursements']
        )

        exp_djangogroups = [e.expensecode.financeproject.costcenter.group for e in self.expenses.all()]
        exp_researchgrps = [g.group_django.first() for g in exp_djangogroups if g.group_django.first() is not None]
        sent_to_groups   = [p.djangogroup for p in perms if p.researchgroup is None or p.researchgroup in exp_researchgrps]

        users = set()
        for g in sent_to_groups:
            for u in g.user_set.all():
                users.add(u)

        for user in users:
            notify(
                'NEW_REIMBURSEMENT_REQUEST',
                '{} submitted a new reimbursement request'.format(self.person),
                '{} submitted a new reimbursement request'.format(self.person),
                user,
                visible=True,
                label='New reimbursement request',
                period='D'
            )

    @property
    def requester_name(self):
        return self.person.full_name if self.person else 'Undefined person'

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
            "draft": '<i class="grey edit outline icon"></i>',
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

        template = "reimbursements/reimbursement_print.html"

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

# from django.conf import settings
# from django.contrib.auth import get_user_model
from confapp import conf
from django.urls import reverse
from pyforms.controls import ControlButton
from ..models import Reimbursement, Expense
from pyforms.basewidget import segment, no_columns
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget
from pyforms.controls import ControlAutoComplete
from supplier.models import FinanceCostCenter, FinanceProject, ExpenseCode

class ExpenseForm(ModelFormWidget):

    MODEL = Expense
    FIELDSETS = [
        ('document_number', "value", "value_currency", "requisition_number"),
        ('_costcenter', '_financeprj', 'expensecode'),
        'receipt',
        'description'
    ]

    def create_model_formfields(self):
        super().create_model_formfields()

        obj = self.model_object

        self._costcenter = ControlAutoComplete(
            'Cost center',
            queryset=FinanceCostCenter.objects.all(),
            changed_event=self.load_finance_projects,
            default=obj.expensecode.financeproject.costcenter.pk
        )
        self._financeprj = ControlAutoComplete(
            'Finance project',
            queryset=FinanceProject.objects.all(),
            enabled=False,
            changed_event=self.load_expense_codes,
            default=obj.expensecode.financeproject.pk
        )

        self.load_expense_codes()


    def load_finance_projects(self):
        self._financeprj.queryset = FinanceProject.objects.filter(costcenter=self._costcenter.value)
        self._financeprj.value = None
        self.expensecode.enabled = False

    def load_expense_codes(self):
        self.expensecode.queryset = ExpenseCode.objects.filter(financeproject=self._financeprj.value)
        self.expensecode.value = None
        self.expensecode.enabled = True



class ExpenseInline(ModelAdminWidget):
    MODEL = Expense
    CLOSE_ON_REMOVE = True

    EDITFORM_CLASS = ExpenseForm

    LIST_DISPLAY = ['document_number',"requisition_number", 'expensecode', "short_description", "value"]
    LIST_HEADERS = ['Document number', 'Requisition number', 'Expense code','Short description', 'Amount']
    LIST_COLS_ALIGN = ["left", "center", "center", "left", "right"]
    LIST_COLS_SIZES = ["5%", "10%", '30%', "40%", "15%"]






class RequestReimbursementForm(ModelFormWidget):
    """
    """

    TITLE = "Request Reimbursement"

    MODEL = Reimbursement

    HAS_CANCEL_BTN_ON_ADD  = False
    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True

    READ_ONLY = ["created", "modified", "status_changed"]

    INLINES = [ExpenseInline]

    # Orquestra ===============================================================
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    # =========================================================================

    def __init__(self, *args, **kwargs):

        self._print = ControlButton(
            '<i class="ui icon print"></i>Print',
            css="basic blue",
            label_visible=False
        )

        super().__init__(*args, **kwargs)

        self.person.enabled = False

        if 'pk' in kwargs:
            url = reverse("print-reimbursement-form", args=[kwargs.get("pk")])
            self._print.value = 'window.open("{0}", "_blank");'.format(url)
        else:
            self._print.hide()
            user   = PyFormsMiddleware.user()
            person = user.person_user.first()
            self.person.value = person.pk
            self.iban.value = person.privateinfo.iban

    def get_fieldsets(self, default):
        formset = [
            no_columns("_print", style="float:right"),
            "h3:Requester Information",
            segment(
                ("person", "iban")
            )
        ]

        if self.object_pk is not None:
            formset += ["h3:Expenses", segment("ExpenseInline")]

        formset += [("created", "modified", "status", "status_changed")]

        return formset

    def get_readonly(self, default):
        res = super().get_readonly(default)
        if not PyFormsMiddleware.user().has_perm('reimbursements.can_approve_reimbursements'):
            return res + ['status']
        else:
            return res


    def update_object_fields(self, obj):
        obj = super().update_object_fields(obj)

        if obj.pk is None:
            obj.created_by = PyFormsMiddleware.user()

        return obj

    def save_event(self, obj, new_object):

        if not new_object and not obj.expenses.count() > 0:
            raise Exception("Add at least one Expense to be reimbursed.")

        return super().save_event(obj, new_object)

    @property
    def title(self):
        if self.model_object:
            name = self.model_object.requester_name
            total = self.model_object.total
            return f"{name} ({total})"
        else:
            return super().title


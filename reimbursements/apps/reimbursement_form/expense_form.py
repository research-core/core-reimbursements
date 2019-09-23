from pyforms_web.widgets.django import ModelFormWidget
from reimbursements.models import Expense
from pyforms.controls import ControlAutoComplete
from supplier.models import FinanceProject, FinanceCostCenter, ExpenseCode
from confapp import conf


class ExpenseForm(ModelFormWidget):

    TITLE = 'Expense form'

    MODEL = Expense
    FIELDSETS = [
        ('document_number', "requisition_number", 'is_social'),
        ' ',
        ('_costcenter', '_financeprj', 'expensecode'),
        ('eur_value', "value", "value_currency"),
        ' ',
        ('receipt_date', ' ', ' '),
        'receipt',
        ' ',
        'description'
    ]

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_WINDOW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.eur_value.changed_event = self.update_value_evt

        if self.object_pk is None:
            self.document_number.value = self.parent.parent.model_object.expenses.count()+1
            self.expensecode.enabled = False
            self._financeprj.enabled = False


    def update_value_evt(self):
        if self.eur_value.value and self.eur_value.value>0 and self.value.value==0:
            self.value.value = self.eur_value.value
            self.value_currency.value = 'EUR'


    def create_model_formfields(self):
        super().create_model_formfields()

        obj  = self.model_object
        person = self.parent_object.person

        self._costcenter = ControlAutoComplete(
            'Cost center',
            queryset=FinanceCostCenter.objects.active().by_person(person),
            changed_event=self.load_finance_projects,
            default=obj.expensecode.financeproject.costcenter.pk if obj and obj.expensecode else None
        )
        self._financeprj = ControlAutoComplete(
            'Finance project',
            queryset=FinanceProject.objects.all(),
            enabled=False,
            changed_event=self.load_expense_codes,
            default=obj.expensecode.financeproject.pk if obj and obj.expensecode else None
        )

        if obj and obj.expensecode:
            self.load_expense_codes()



    def load_finance_projects(self):
        self._financeprj.queryset = FinanceProject.objects.filter(costcenter=self._costcenter.value)
        self._financeprj.value = None
        self._financeprj.enabled = True
        self.expensecode.enabled = False

    def load_expense_codes(self):
        self.expensecode.queryset = ExpenseCode.objects.filter(financeproject=self._financeprj.value)
        self.expensecode.value = None
        self.expensecode.enabled = True





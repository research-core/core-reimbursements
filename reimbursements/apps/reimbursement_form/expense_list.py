from reimbursements.models import Expense
from pyforms_web.widgets.django import ModelAdminWidget
from .expense_form import ExpenseForm

class ExpenseInline(ModelAdminWidget):
    MODEL = Expense
    CLOSE_ON_REMOVE = True

    EDITFORM_CLASS = ExpenseForm

    LIST_DISPLAY = ['document_number',"requisition_number", 'expensecode', "short_description", "value"]
    LIST_HEADERS = ['Document number', 'Requisition number', 'Expense code','Short description', 'Amount']
    LIST_COLS_ALIGN = ["left", "center", "center", "left", "right"]
    LIST_COLS_SIZES = ["5%", "10%", '30%', "40%", "15%"]

    USE_DETAILS_TO_EDIT = False
    USE_DETAILS_TO_ADD =  False


    def has_add_permissions(self):
        obj = self.parent_model.objects.get(pk=self.parent_pk)
        return obj.status in ['draft', 'pending']

    def has_update_permissions(self, obj):
        obj = obj.reimbursement
        return obj.status in ['draft', 'pending']

    def has_remove_permissions(self, obj):
        obj = obj.reimbursement
        return obj.status in ['draft', 'pending']
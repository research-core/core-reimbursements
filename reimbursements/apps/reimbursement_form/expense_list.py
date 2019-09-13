from pyforms.basewidget import no_columns
from reimbursements.apps.reimbursement_form.per_diem_form import PerDiemForm
from reimbursements.models import Expense, PerDiem
from pyforms_web.widgets.django import ModelAdminWidget
from .expense_form import ExpenseForm
from pyforms.controls import ControlButton

class ExpenseInline(ModelAdminWidget):
    MODEL = Expense
    CLOSE_ON_REMOVE = True

    EDITFORM_CLASS = ExpenseForm

    LIST_DISPLAY = ['document_number',"requisition_number", 'expensecode', "short_description", "value"]
    LIST_HEADERS = ['Document number', 'Requisition number', 'Expense code','Short description', 'Amount']
    LIST_COLS_ALIGN = ["left", "center", "center", "left", "right"]
    LIST_COLS_SIZES = ["5%", "10%", '30%', "40%", "15%"]

    USE_DETAILS_TO_EDIT = False
    USE_DETAILS_TO_ADD  = False

    ADD_BTN_LABEL = '<i class="plus icon"></i> Add expense'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_perdiem = ControlButton('<i class="plus icon"></i> Add per diem', default=self.__add_perdiem_evt, label_visible=False, css='tiny basic blue')

    def get_toolbar_buttons(self, has_add_permission=False):
        return no_columns('_add_btn', '_add_perdiem') if has_add_permission else None

    def __add_perdiem_evt(self):
        params = {
            'title': 'Create',
            'model': PerDiem,
            'parent_model': self.parent_model,
            'parent_pk': self.parent_pk,
            'parent_win': self
        }
        createform = PerDiemForm(**params)

    def has_add_permissions(self):
        return self.parent.has_update_permissions()

    def has_update_permissions(self, obj):
        res = super().has_update_permissions(obj)
        if res:
            obj = obj.reimbursement
            return obj.status in ['draft', 'pending']
        else:
            return res


    def has_remove_permissions(self, obj):
        res = super().has_remove_permissions(obj)
        if res:
            obj = obj.reimbursement
            return obj.status in ['draft', 'pending']
        else:
            return res

    def get_editmodel_class(self, obj):

        if obj.perdiem:
            return PerDiemForm
        else:
            return super().get_editmodel_class(obj)
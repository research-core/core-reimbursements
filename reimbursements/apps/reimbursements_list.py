from pyforms_web.widgets.django import ModelAdminWidget
from .reimbursement_form import RequestReimbursementForm
from pyforms_web.web.middleware import PyFormsMiddleware
from ..models import Reimbursement
from confapp import conf

class ReimbursementsApp(ModelAdminWidget):
    """
    """

    UID = "reimbursements"
    TITLE = "Reimbursements"

    MODEL = Reimbursement
    EDITFORM_CLASS = RequestReimbursementForm

    USE_DETAILS_TO_ADD  = False
    USE_DETAILS_TO_EDIT = False

    LIST_DISPLAY = [
        "created_by",
        "get_requisitions_status",
        "total",
        "status",
    ]
    LIST_FILTER = ["created", "status"]
    SEARCH_FIELDS = ["person__full_name__icontains", "ext_person_name__icontains"]

    # Orquestra ===============================================================
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = "top"
    ORQUESTRA_MENU_ICON = "file alternate outline"
    ORQUESTRA_MENU_ORDER = 800
    # =========================================================================

    def __init__(self, *args, **kwargs):
        self.user = PyFormsMiddleware.user()
        super().__init__(*args, **kwargs)

        self._list.columns_size = ["60%", "10%", "10%", "10%", "10%"]

        self._list.columns_align = ["left"] * len(self.LIST_DISPLAY)
        self._list.columns_align[-2] = "right"
        self._list.columns_align[-1] = "center"


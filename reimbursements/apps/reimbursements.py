# from django.conf import settings
# from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from confapp import conf

from pyforms.basewidget import segment, no_columns

from pyforms.controls import ControlButton

# from pyforms_web.basewidget import BaseWidget
# from pyforms_web.controls.control_button import ControlButton
# from pyforms_web.controls.control_template import ControlTemplate
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelAdminWidget
from pyforms_web.widgets.django import ModelFormWidget

from humanresources.models import Person
from ..models import Reimbursement, Expense


class ExpenseInline(ModelAdminWidget):
    MODEL = Expense

    CLOSE_ON_REMOVE = True

    LIST_DISPLAY = ["requisition_number", "short_description", "value"]

    FIELDSETS = [("value", "value_currency", "requisition_number"), "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._list._columns_align = ["left", "left", "right"]
        self._list._columns_size = ["15%", "70%", "15%"]


class ReimbursementForm(ModelFormWidget):
    ...


class RequestReimbursementForm(ReimbursementForm):
    """
    """

    TITLE = "Request Reimbursement"

    MODEL = Reimbursement

    HAS_CANCEL_BTN_ON_ADD = False
    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True

    READ_ONLY = ["created", "modified", "status_changed"]

    INLINES = [ExpenseInline]

    # Orquestra ===============================================================
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    # =========================================================================

    def __init__(self, *args, **kwargs):
        self.user = PyFormsMiddleware.user()

        super().__init__(*args, **kwargs)

        url = reverse("print-reimbursement-form", args=[kwargs.get("pk")])

        self._print = ControlButton(
            '<i class="ui icon print"></i>Print',
            default='window.open("{0}", "_blank");'.format(url),
            css="basic blue",
            label_visible=False,
        )

        person = self.user.person_user.first()

        if person is not None:
            print("setting person to", person)
            self.person.value = person.pk
            # self.person.value = Person.objects.get(pk=person.pk)
            # self.model_object.person = Person.objects.get(pk=person.pk)

        if not self.user.has_perm("can_request_for_other"):
            self.person.enabled = False
            self.ext_person_name.hide()
            self.ext_person_iban.hide()

    def get_fieldsets(self, default):
        toolbar_segment = [no_columns("_print", style="float:right")]
        main_segment = [
            "h3:Requester Information",
            segment(("person", "ext_person_name", "ext_person_iban"), "project"),
        ]
        expenses_segment = ["h3:Expenses", segment("ExpenseInline")]
        management_segment = [("created", "modified", "status", "status_changed")]

        default = toolbar_segment + main_segment + expenses_segment + management_segment

        # if self.user.has_perm("can_request_for_other"):
        #     default.insert(0, person_segment)

        return default

    def get_readonly(self, default):

        # if self.user.has_perm("can_request_for_other"):
        #     default.remove("person")

        return default

    def update_object_fields(self, obj):
        obj = super().update_object_fields(obj)
        print(obj.__dict__)
        print(self.user, type(self.user), self.user.pk)
        if obj.created_by_id is None:
            obj.created_by_id = self.user.pk
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


class ReimbursementsApp(ModelAdminWidget):
    """
    """

    UID = "reimbursements"
    TITLE = "Reimbursements"

    MODEL = Reimbursement
    EDITFORM_CLASS = RequestReimbursementForm

    USE_DETAILS_TO_ADD = False
    USE_DETAILS_TO_EDIT = False

    LIST_DISPLAY = [
        "requester_name",
        "get_project_code",
        "get_requisitions_status",
        "total",
        "status_icon",
    ]
    LIST_FILTER = ["created", "status", "project"]
    SEARCH_FIELDS = ["person__full_name__icontains", "ext_person_name__icontains"]

    # Orquestra ===============================================================
    LAYOUT_POSITION = conf.ORQUESTRA_HOME
    ORQUESTRA_MENU = "left"
    ORQUESTRA_MENU_ICON = "file alternate outline"
    ORQUESTRA_MENU_ORDER = 800
    # =========================================================================

    def __init__(self, *args, **kwargs):
        self.user = PyFormsMiddleware.user()
        super().__init__(*args, **kwargs)

        self._list._columns_size = ["60%", "10%", "10%", "10%", "10%"]

        self._list._columns_align = ["left"] * len(self.LIST_DISPLAY)
        self._list._columns_align[-2] = "right"
        self._list._columns_align[-1] = "center"

    def has_remove_permissions(self, obj):
        if obj:
            return obj.status == "pending" and obj.created_by == self.user
        return False

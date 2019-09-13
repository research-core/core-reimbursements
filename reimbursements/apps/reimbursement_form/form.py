from django.utils import timezone

from common.models import Permissions
from confapp import conf
from django.db.models import Q
from django.urls import reverse
from pyforms.controls import ControlButton
from reimbursements.models import Reimbursement
from pyforms.basewidget import segment, no_columns
from pyforms_web.web.middleware import PyFormsMiddleware
from pyforms_web.widgets.django import ModelFormWidget
from .expense_list import ExpenseInline



class RequestReimbursementForm(ModelFormWidget):
    """
    """

    TITLE = "Request Reimbursement"

    MODEL = Reimbursement

    HAS_CANCEL_BTN_ON_ADD  = False
    HAS_CANCEL_BTN_ON_EDIT = False
    CLOSE_ON_REMOVE = True

    READ_ONLY = ["created", "modified", "status_changed", 'status']

    INLINES = [ExpenseInline]

    FIELDSETS = [
        no_columns('_previous', '_submit', "_print", '_printed', '_submit2approve','_reject', '_accept', 'bank_transfer_date', '_close', style="float:right"),
        "h3:Requester Information",
        segment(
            ("person", "iban"),
            'fullname',
    ),
        "h3:Expenses",
        segment("ExpenseInline"),
        ("created", "modified", "status", "status_changed")
    ]

    # Orquestra ===============================================================
    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    # =========================================================================

    def __init__(self, *args, **kwargs):


        self._previous = ControlButton(
            '<i class="ui icon paper plane outline"></i>Previous status',
            css="basic gray",
            visible = False,
            label_visible=False,
            default = self.__previous_status_evt
        )

        self._submit = ControlButton(
            '<i class="ui icon paper plane outline"></i>Submit',
            css="blue",
            visible=False,
            label_visible=False,
            default = self.__submit_2_pending_evt
        )

        self._print = ControlButton(
            '<i class="ui icon print"></i>Print',
            visible=False,
            css="basic blue",
            label_visible=False
        )

        self._printed = ControlButton(
            '<i class="ui icon paper plane outline"></i>Set printed',
            visible=False,
            css="blue",
            label_visible=False,
            default=self.__set_printed_evt
        )

        self._submit2approve = ControlButton(
            '<i class="ui icon paper plane outline"></i>Submit to approval',
            visible=False,
            css="blue",
            label_visible=False,
            default=self.__submit_2_approve_evt
        )

        self._accept = ControlButton(
            '<i class="ui icon thumbs up"></i>Accept',
            visible=False,
            css="green",
            label_visible=False,
            default = self.__accept_evt
        )

        self._reject = ControlButton(
            '<i class="ui icon thumbs down"></i>Reject',
            visible=False,
            css="red",
            label_visible=False,
            default=self.__reject_evt
        )

        self._close = ControlButton(
            '<i class="ui icon thumbs up"></i>It was paid',
            visible=False,
            css="green basic",
            default=self.__set_closed_evt
        )



        super().__init__(*args, **kwargs)


        # Check if the user has permissions to create a reimbursement on behalf of other people
        user = PyFormsMiddleware.user()
        self.person.enabled = Permissions.objects.filter_by_user_and_auth_permissions(
            user, Reimbursement, ['create_reimbursements_on_behalf_others']
        ).exists()

        # Select the person automatically
        if self.model_object is None:
            person = user.person_user.first()

            if person is not None:
                self.person.value = person.pk
                self.iban.value = person.privateinfo.iban

            elif not self.person.enabled:
                self.warning(
                    'You need a Person profile associated to your account to be able to create reimbursements.'
                )

        self.update_fields_visibility()



    def autocomplete_search(self, queryset, keyword, control):
        queryset = super().autocomplete_search(queryset, keyword, control)

        if control.name=='person':
            user = PyFormsMiddleware.user()

            ranked_permissions = Permissions.objects.filter_by_user_and_auth_permissions(
                user, Reimbursement, ['create_reimbursements_on_behalf_others']
            )

            if ranked_permissions.exists():
                # check if the user has permissions to all registers
                if ranked_permissions.filter(researchgroup=None).exists():
                    return queryset
                else:
                    # check which people the user has permissions to
                    researchgroups = [p.researchgroup for p in ranked_permissions]

                    # The owner of the reimbursements or the manager of the expense codes can access
                    now = timezone.now()

                    return queryset.filter(
                        Q(djangouser=user) | (
                            Q(groupmember__group__in=researchgroups) &
                            (
                                Q(groupmember__date_joined__lte=now) | Q(groupmember__date_joined=None)
                            ) &
                            (
                                Q(groupmember__date_left__gte=now) | Q(groupmember__date_left=None)
                            )
                        )
                    )

        return queryset.filter(pk=0)

    def update_fields_visibility(self):
        obj = self.model_object

        if obj:
            self._print.value = 'window.open("{0}", "_blank");'.format(
                reverse("print-reimbursement-form", args=[obj.pk])
            )
            self._print.show()
        else:
            # show print button only when the reimbursement is pending
            self._print.hide()

        # show submit button only when is draft
        if obj is None or obj.status != 'draft':
            self._submit.hide()

        if obj and self.has_update_permissions():

            if obj.status == 'draft':

                self.bank_transfer_date.hide()
                self._submit.show()
                self._previous.hide()
                self._print.hide()
                self._printed.hide()
                self._submit2approve.hide()
                self._accept.hide()
                self._reject.hide()
                self._close.hide()
                self.iban.enabled = True

            elif obj.status == 'pending':

                self.bank_transfer_date.hide()
                self._previous.show()
                self._submit.hide()
                self._print.show()
                self._printed.show()
                self._submit2approve.hide()
                self._accept.hide()
                self._reject.hide()
                self._close.hide()
                self.iban.enabled = False

            elif obj.status == 'printed':

                self.bank_transfer_date.hide()
                self._previous.show()
                self._submit.hide()
                self._print.hide()
                self._printed.hide()
                self._submit2approve.show()
                self._accept.hide()
                self._reject.hide()
                self._close.hide()
                self.iban.enabled = False

            elif obj.status == 'submitted':

                self.bank_transfer_date.hide()
                self._previous.show()
                self._submit.hide()
                self._print.hide()
                self._printed.hide()
                self._submit2approve.hide()
                self._accept.show()
                self._reject.show()
                self._close.hide()
                self.iban.enabled = False

            elif obj.status in ['rejected', 'approved']:

                self._previous.hide()
                self._submit.hide()
                self._print.hide()
                self._printed.hide()
                self._submit2approve.hide()
                self._accept.hide()
                self._reject.hide()
                self.iban.enabled = False

                if obj.status == 'approved':
                    self.bank_transfer_date.show()
                    self._close.show()
                else:
                    self.bank_transfer_date.hide()
                    self._close.hide()

            elif obj.status == 'closed':

                self.bank_transfer_date.show()
                self.bank_transfer_date.readonly = True
                self._previous.hide()
                self._submit.hide()
                self._print.hide()
                self._printed.hide()
                self._submit2approve.hide()
                self._accept.hide()
                self._reject.hide()
                self._close.hide()
                self.iban.enabled = False

        else:

            self.bank_transfer_date.hide()
            self._submit.hide()
            self._previous.hide()
            self._print.hide()
            self._printed.hide()
            self._submit2approve.hide()
            self._accept.hide()
            self._reject.hide()
            self._close.hide()
            self.iban.enabled = True





    def save_btn_event(self):
        super().save_btn_event()
        self.update_fields_visibility()

    def __previous_status_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.previous_status()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __set_printed_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.set_printed()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __submit_2_pending_evt(self):
        """
        Notify the users with approval responsibility about the new reimbursement
        """
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.submit_to_pending()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __submit_2_approve_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.submit_for_approval()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __accept_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.accept()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __reject_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.reject()

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()

    def __set_closed_evt(self):
        if not self.has_update_permissions():
            raise Exception('No permission')

        obj = self.model_object
        obj.bank_transfer_date = self.bank_transfer_date.value
        obj.set_closed() # this function will save the object

        self.show_edit_form(self.object_pk)
        self.update_fields_visibility()


    def get_readonly(self, default):
        res  = super().get_readonly(default)
        obj  = self.model_object

        if obj and obj.status in ['rejected', 'approved']:
            return res + ['status']

        if obj and obj.has_approve_permissions(PyFormsMiddleware.user()):
            return res
        else:
            return res + ['status']


    def update_object_fields(self, obj):
        """
        Update the created by field.
        :param Reimbursement obj:
        :return: Return the updated reimbursement object.
        """
        obj = super().update_object_fields(obj)

        if obj.pk is None:
            obj.created_by = PyFormsMiddleware.user()

        return obj

    @property
    def title(self):
        obj = self.model_object
        if obj:
            name = obj.requester_name
            total = obj.total
            return f"({obj.pk}) {obj.person} ({obj.total})"
        else:
            return super().title


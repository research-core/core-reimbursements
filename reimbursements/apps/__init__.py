from django.apps import AppConfig


class ReimbursementsConfig(AppConfig):

    name = "reimbursements"

    def ready(self):
        # Import PyForms apps
        from .reimbursements_list import ReimbursementsApp
        from .reimbursement_form import RequestReimbursementForm

        #  and place them in the global scope
        global ReimbursementsApp
        global RequestReimbursementForm

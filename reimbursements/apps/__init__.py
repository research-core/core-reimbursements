from django.apps import AppConfig


class ReimbursementsConfig(AppConfig):
    name = "reimbursements"

    def ready(self):
        # Import PyForms apps
        from .reimbursements import ReimbursementsApp
        from .reimbursements import RequestReimbursementForm

        #  and place them in the global scope
        global ReimbursementsApp
        global RequestReimbursementForm

from django.core.exceptions import PermissionDenied

from reimbursements.models import Reimbursement


def print_reimbursement_form(request, reimbursement_id):
    reimbursement = Reimbursement.objects.get(pk=reimbursement_id)
    return reimbursement.generate_pdf_view(request)

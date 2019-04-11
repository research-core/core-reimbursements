from . import views
from django.urls import path

urlpatterns = [
    path("print-reimbursement/<int:reimbursement_id>/", views.print_reimbursement_form, name="print-reimbursement-form")
]

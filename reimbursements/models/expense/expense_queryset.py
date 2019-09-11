from django.db import models
from django.db.models import Q
from common.models import Permissions
from reimbursements.models import Reimbursement
from supplier.models import ExpenseCode

class ExpenseQuerySet(models.QuerySet):
    # User dependent Querysets
    # =========================================================================

    def owned_by(self, user):
        """
        Filters the Queryset to objects owned by the User or where
        he is referenced in a Foreign Key.

        This is by default what everyone sees if they have no permissions.
        """
        return self.filter( Q(reimbursement__created_by=user) | Q(reimbursement__person__djangouser=user) ).distinct()

    def managed_by(self, user, required_codenames, default=None):
        """
        Filters the Queryset to objects the user is allowed to manage
        given his Authorization Group profiles.

        Uses the RankedPermissions table.
        """
        if default is None:
            default = self.none()

        if user.is_superuser:
            return self

        ranked_permissions = Permissions.objects.filter_by_user_and_auth_permissions(
            user, Reimbursement, required_codenames)

        if ranked_permissions.exists():
            # check if the user has permissions to all registers
            if ranked_permissions.filter(researchgroup=None).exists():
                return self
            else:
                # check which expense codes the user has permissions to
                researchgroups = [p.researchgroup for p in ranked_permissions]
                djangogroups   = [g.groupdjango for g in researchgroups]
                expenses_with_access = ExpenseCode.objects.filter(
                    reimbursement__financeproject__costcenter__group__in=djangogroups
                )

                # The owner of the reimbursements or the manager of the expense codes can access
                return self.filter(
                    Q(expensecode__in=expenses_with_access) |
                    Q(reimbursement__created_by=user) |
                    Q(reimbursement__person__djangouser=user)
                )

        return default.distinct()



    # PyForms Querysets

    def list_permissions(self, user):
        return self.managed_by(
            user,
            ['can_approve_reimbursements', 'manage_reimbursements', 'receive_approved_notifications', 'view_reimbursement'],
            default=self.owned_by(user)
        )

    def has_add_permissions(self, user):
        return self.has_update_permissions(user)

    def has_view_permissions(self, user):
        # view_permission is useless because we let people see
        # their own objects via list_permissions
        return self.list_permissions(user)

    def has_update_permissions(self, user):

        # it was created or belongs to the user.
        if self.filter(
                Q(reimbursement__status="draft") &
                (
                    Q(reimbursement__created_by=user) | Q(reimbursement__person__djangouser=user)
                )
            ).exists():
            return True

        if self.filter(
                reimbursement__status__in=['draft', 'pending', 'printed', 'approved', 'rejected']
            ).managed_by( user, ['manage_reimbursements'] ).exists():
            return True

        if self.filter( reimbursement__status__in=['submitted'] ).managed_by( user, ['can_approve_reimbursements'] ).exists():
            return True

        return False

    def has_remove_permissions(self, user):
        """
        Only reimbursements in draft or pending can be removed.
        """
        return self.filter(
            Q(reimbursement__status__in=["draft", "pending"]) & ( Q(reimbursement__created_by=user) | Q(reimbursement__person__djangouser=user) )
        )




    # =========================================================================

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.utils import timezone


from common.models import Permissions


class ReimbursementQuerySet(models.QuerySet):
    pass
    # User dependent Querysets
    # =========================================================================

    def owned_by(self, user):
        """
        Filters the Queryset to objects owned by the User or where
        he is referenced in a Foreign Key.

        This is by default what everyone sees if they have no permissions.
        """
        return self.filter(
            Q(person__djangouser=user)
            |
            Q(created_by=user)
        ).distinct()

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

        ranked_permissions = Permissions.objects.filter_by_auth_permissions(
            user, self.model, required_codenames)

        if ranked_permissions.exists():
            # check if the user has permissions to all people
            if ranked_permissions.filter(researchgroup=None).exists():
                return self
            else:

                # check which groups the user has to its people
                groups_withaccess = [p.researchgroup for p in ranked_permissions]
                return self.filter(person__group_set=groups_withaccess)

        return default.distinct()

    # PyForms Querysets

    def list_permissions(self, user):
        return self.managed_by(
            user,
            ['can_approve_reimbursements'],
            default=self.owned_by(user)
        )

    def has_add_permissions(self, user):
        return True

    def has_view_permissions(self, user):
        # view_permission is useless because we let people see
        # their own objects via list_permissions
        return self.list_permissions(user)

    def has_update_permissions(self, user):
        default = self.filter(
            Q(status="pending") &
            (
                    Q(created_by=user) |
                    Q(person__djangouser=user)
            )
        )

        return self.managed_by(
            user,
            ['can_approve_reimbursements'],
            default=default
        ).exists()


    def has_remove_permissions(self, user):
        return self.filter(
            Q(status="pending") &
            (
                    Q(created_by=user) |
                    Q(person__djangouser=user)
            )
        )

    # =========================================================================
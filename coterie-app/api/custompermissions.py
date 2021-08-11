from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project, Team, Enrollments
from .utils import Status as user_status, Roles
# -> only team members can view a project
# -> only project creator and team owner can delete project
# -> when you're in a team and ur role is not viewer, u can update a project


class hasTeamDetailPermissions(BasePermission):
    message = "you do not have permission to perform this action."

    def has_permission(self, request, view):
        # you have to be a team member to see projects -> Team owner or member with status Accepted
        is_owner = Team.objects.filter(
            owner=request.user.id, id=view.kwargs['team_id']).exists()
        is_member = Team.objects.filter(
            id=view.kwargs['team_id'], members__id=request.user.id).exists()

        is_verified_member = False
        is_not_viewer = False
        has_owner_priviledge = False

        if is_member:
            self.message = "please accept team invite first."
            team_status_obj = Enrollments.objects.get(
                team=view.kwargs['team_id'], user=request.user.id)
            is_verified_member = team_status_obj.status == user_status.ACCEPTED
            if is_verified_member:
                is_not_viewer = team_status_obj.role != Roles.VIEWER
                has_owner_priviledge = team_status_obj.role == Roles.OWNER

        if request.method in SAFE_METHODS:
            # if you are a member, your status has to accepted not pending

            return is_owner or is_verified_member

        if request.method in ['PUT', 'PATCH']:
            return is_owner or is_not_viewer

        if request.method in ['DELETE']:

            # -> no admin priviledge here: request.user.is_superuser
            return is_owner or has_owner_priviledge


class IsOwnerOrContributor(BasePermission):
    """this permission decides who can create, modify, or delete a project in a team."""

    message = "you do not have permission to perform this action."

    def has_permission(self, request, view):
        # you have to be a team member to see projects -> Team owner or member with status Accepted
        is_owner = Team.objects.filter(
            owner=request.user.id, id=view.kwargs['team_id']).exists()
        is_member = Team.objects.filter(
            id=view.kwargs['team_id'], members__id=request.user.id).exists()

        if is_member:
            self.message = "please accept team invite first."
            team_status_obj = Enrollments.objects.get(
                team=view.kwargs['team_id'], user=request.user.id)
            is_verified_member = team_status_obj.status == user_status.ACCEPTED
            if is_verified_member:
                is_not_viewer = team_status_obj.role != Roles.VIEWER
                has_owner_priviledge = team_status_obj.role == Roles.OWNER
        else:
            is_verified_member = False
            is_not_viewer = False
            has_owner_priviledge = False

        if request.method in SAFE_METHODS:

            return is_owner or is_verified_member

        if request.method in ['POST']:
            self.message = "only user with owner priviledge can perform this action"
            return is_owner or has_owner_priviledge

        if request.method in ['PUT', 'PATCH']:
            self.message = "only team owners and contributors can perform this action"
            # you have to be an owner or contributor to create update project
            # -> no admin priviledge here: request.user.is_superuser
            return is_owner or is_not_viewer

        if request.method == 'DELETE':
           # DELETE -> owner , creator
            self.message = "only user with owner priviledge can perform this action"
            return is_owner or has_owner_priviledge


class CanInviteUser(BasePermission):
    """only owner and user with owner privildege can ivite or delete an invited member"""
    message = "only team members and owners have this permission"

    def has_permission(self, request, view):
        is_owner = Team.objects.filter(
            owner=request.user.id, id=view.kwargs['team_id']).exists()
        is_member = Team.objects.filter(
            id=view.kwargs['team_id'], members__id=request.user.id).exists()

        if is_member:
            self.message = "please accept team invite first."
            team_status_obj = Enrollments.objects.get(
                team=view.kwargs['team_id'], user=request.user.id)
            is_verified_member = team_status_obj.status == user_status.ACCEPTED
            if is_verified_member:
                has_owner_priviledge = team_status_obj.role == Roles.OWNER
        else:
            is_verified_member = False
            has_owner_priviledge = False

        if request.method in SAFE_METHODS:
            return is_owner or is_verified_member

        else:
            self.message = "only user with owner priviledge can perform this action"
            return is_owner or has_owner_priviledge


class IsAdminUserOrReadonly(BasePermission):
    message = "only admins can create or modify models"

    def has_permission(self, request, view):
        is_admin = request.user.is_superuser
        if request.method in SAFE_METHODS:
            return True
        return is_admin

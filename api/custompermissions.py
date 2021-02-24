from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Project, Team, Enrollments
from .utils import Status as user_status, Roles
#-> only team members can view a project
#-> only project creator and team owner can delete project
# -> when you're in a team and ur role is not viewer, u can update a project

class IsTeamMember(BasePermission):
    message = "you do not have permission to perform this action."
    def has_permission(self, request, view):
        #you have to be a team member to see projects -> Team owner or member with status Accepted
        

        if request.method in SAFE_METHODS:
            #find owner
            is_owner = Team.objects.filter(owner=request.user.id, id=view.kwargs['team_id']).exists()

            if is_owner:
                return True

            #find member
            is_member = Team.objects.filter(id=view.kwargs['team_id'], members__id=request.user.id).exists()

            # if you are a member, your status has to accepted not pending
            if is_member:
                self.message = "please accept team invite first."
                team_status_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                is_verified_member = team_status_obj.status == user_status.ACCEPTED
                
                return is_verified_member

            return False

        else:
            #you have to be a team owner to create project
            is_owner = Team.objects.filter(id=view.kwargs['team_id'], owner=request.user.id).exists()
            if is_owner:
                return True

            #a member can have owner priviledge
            is_member = Team.objects.filter(id=view.kwargs['team_id'], members__id=request.user.id).exists()

            if is_member:
                team_role_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                has_owner_priviledge = team_role_obj.role == Roles.OWNER
                return has_owner_priviledge

            return False # -> no admin priviledge here: request.user.is_superuser

class IsOwnerOrContributor(BasePermission):
    message = "you do not have permission to perform this action." 

    def has_permission(self, request, view):
        #you have to be a team member to see projects -> Team owner or member with status Accepted
        

        if request.method in SAFE_METHODS:
            #find owner
            is_owner = Team.objects.filter(owner=request.user.id, id=view.kwargs['team_id']).exists()

            if is_owner:
                return True

            #find member
            is_member = Team.objects.filter(id=view.kwargs['team_id'], members__id=request.user.id).exists()

            # if you are a member, your status has to accepted not pending
            if is_member:
                self.message = "please accept team invite first."
                team_status_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                is_verified_member = team_status_obj.status == user_status.ACCEPTED
                
                return is_verified_member

            return False

        else:
            #you have to be a team owner to create project
            is_owner = Team.objects.filter(id=view.kwargs['team_id'], owner=request.user.id).exists()
            if is_owner:
                return True

            #a member can have owner priviledge
            is_member = Team.objects.filter(id=view.kwargs['team_id'], members__id=request.user.id).exists()

            if is_member:
                team_role_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                is_verified_member = team_role_obj.status == user_status.ACCEPTED

                if is_verified_member:
                    self.message = "please accept team invite first."
                    is_not_viewer = team_role_obj.role != Roles.VIEWER
                    return is_not_viewer
                    
                return False

            return False # -> no admin priviledge here: request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        #find owner
        is_owner = Team.objects.filter(owner=request.user.id, id=view.kwargs['team_id']).exists()

        #find member
        is_member = Team.objects.filter(id=view.kwargs['team_id'], members__id=request.user.id).exists()

        #find creator
        is_creator = request.user == obj.creator

        if request.method in SAFE_METHODS:
            #you have to be a team member to view detail
            if is_owner:
                return True

            # if you are a member, your status has to accepted not pending
            if is_member:
                self.message = "please accept team invite first."
                team_status_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                is_verified_member = team_status_obj.status == user_status.ACCEPTED
                
                return is_verified_member
            return False

        if request.method in ['PUT', 'PATCH']:
            # PUT, PATCH -> owner, creator, contributor
            if is_owner or is_creator:
                return True
            if is_member:
                #also check user has accepted invite
                team_role_obj = Enrollments.objects.get(team=view.kwargs['team_id'], user=request.user.id)
                is_verified_member = team_role_obj.status == user_status.ACCEPTED

                if is_verified_member:
                    self.message = "please accept team invite first."
                    is_not_viewer = team_role_obj.role != Roles.VIEWER
                    return is_not_viewer
                return False
            return False

        if request.method == 'DELETE':
            # DELETE -> owner , creator
            
            return is_owner or is_creator
        return False
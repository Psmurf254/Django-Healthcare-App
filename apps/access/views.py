from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView
from apps.asset_manager.forms import RoleForm, AssignPermissionsForm
from web_project import TemplateLayout


class AccessView(PermissionRequiredMixin, TemplateView):
    permission_required = (
        "permission.view_permission", "permission.delete_permission", "permission.change_permission",
        "permission.add_permission"
    )
    template_name = "app_access_roles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize template layout context
        context = TemplateLayout.init(self, context)

        groups = Group.objects.all()
        context['roles'] = groups
        context['total_roles'] = groups.count()
        users = User.objects.all()
        context['users'] = users

        # User-role mappings with admin role for superusers
        user_roles = {}
        for user in users:
            roles = list(user.groups.all())
            if user.is_superuser:
                admin_group = Group(name='admin')
                roles.append(admin_group)
            user_roles[user] = roles

        context['user_roles'] = user_roles

        permissions = Permission.objects.all()
        context['permissions'] = permissions

        groups_with_users = {group: group.user_set.all() for group in groups}
        context['groups_with_users'] = groups_with_users
        context['role_form'] = kwargs.get('role_form', RoleForm())
        context['assign_permissions_form'] = AssignPermissionsForm()

        return context
    
    def role_exists(self, role_name):
        return Group.objects.filter(name=role_name).exists()

    def get(self, request, *args, **kwargs):
        role_id = request.GET.get('role_id')
        if role_id:
            role = get_object_or_404(Group, id=role_id)
            role_form = RoleForm(instance=role)
            context = self.get_context_data(role_form=role_form, role_id=role_id)
        else:
            context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        role_id = request.POST.get('role_id')
        if role_id:
            role = get_object_or_404(Group, id=role_id)
            role_form = RoleForm(request.POST, instance=role)
        else:
            role_form = RoleForm(request.POST)

        if role_form.is_valid():
            role = role_form.save(commit=False)
            role.save()
            permissions = request.POST.getlist('permissions')
            if 'all' in permissions:
                all_permissions = Permission.objects.all()
                role.permissions.set(all_permissions)
            else:
                selected_permissions = Permission.objects.filter(id__in=permissions)
                role.permissions.set(selected_permissions)

            selected_users = request.POST.getlist('users')
            role.user_set.set(selected_users)

            messages.success(request, 'Role saved successfully')
            return redirect('app-access-roles')
        else:
            messages.error(request, 'Failed to save the role')
            return redirect('app-access-roles')


class AccessUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = (
        "permission.view_permission", "permission.delete_permission", "permission.change_permission",
        "permission.add_permission"
    )
    template_name = "app_access_roles_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        role_id = kwargs.get('role_id')
        role = get_object_or_404(Group, id=role_id)
        context['role'] = role

        users = User.objects.all()

        # get all user roles
        context['users'] = users

        permissions = Permission.objects.all()
        context['permissions'] = permissions

        context['role_form'] = kwargs.get('role_form', RoleForm(instance=role))
        context['assign_permissions_form'] = AssignPermissionsForm()

        return context

    def post(self, request, *args, **kwargs):
        role_id = kwargs.get('role_id')
        role = get_object_or_404(Group, id=role_id)
        role_form = RoleForm(request.POST, instance=role)
        if role_form.is_valid():
            role.save()
            permissions = request.POST.getlist('permissions')
            if 'all' in permissions:
                all_permissions = Permission.objects.all()
                role.permissions.set(all_permissions)
            else:
                selected_permissions = Permission.objects.filter(id__in=permissions)
                role.permissions.set(selected_permissions)

            selected_users = request.POST.getlist('users')
            role.user_set.set(selected_users)

            messages.success(request, 'Role saved successfully')
            return redirect('app-access-roles')
        else:
            messages.error(request, 'Failed to save the role')
            return redirect('app-access-roles')


class AccessDeleteView(PermissionRequiredMixin, TemplateView):
    permission_required = (
        "permission.delete_permission"
    )

    def get(self, request, role_id):
        role = get_object_or_404(Group, id=role_id)
        role.delete()
        messages.success(request, 'Role Deleted')
        return redirect('app-access-roles')


class UserUpdateStatus(PermissionRequiredMixin, TemplateView):
    permission_required = (
        "permission.change_permission"
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.is_superuser:
            messages.error(request, 'Superusers cannot be deactivated.')
        else:
            # Toggle the user's active status
            if user.is_active:
                user.is_active = False
                messages.success(request, f'{user.username} has been deactivated.')
            else:
                user.is_active = True
                messages.success(request, f'{user.username} has been activated.')
            user.save()

        return redirect('app-access-roles')

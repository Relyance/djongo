from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import User


# View to create a user
@require_POST
def create_user(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    user_type = request.POST.get('user_type', '')

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required'}, status=400)

    try:
        user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name,
                                        user_type=user_type)
        return JsonResponse({'message': 'User created successfully', 'user_id': user.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# View to login a user
@require_POST
def login_user(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(request, email=email, password=password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({'message': 'Logged in successfully'})
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)


# View to delete a user
@login_required
@require_POST
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'message': 'User deleted successfully'})


# Add a user to a group
@login_required
@require_POST
def add_user_to_group(request, user_id, group_name):
    user = get_object_or_404(User, id=user_id)
    group, created = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    return JsonResponse({'message': f'User {user.email} added to group {group_name}'})


# Remove a user from a group
@login_required
@require_POST
def remove_user_from_group(request, user_id, group_name):
    user = get_object_or_404(User, id=user_id)
    group = get_object_or_404(Group, name=group_name)
    user.groups.remove(group)
    return JsonResponse({'message': f'User {user.email} removed from group {group_name}'})


# Add permissions to a user
@login_required
@require_POST
def add_permission_to_user(request, user_id, perm_codename):
    user = get_object_or_404(User, id=user_id)
    print(perm_codename)
    permission = get_object_or_404(Permission, codename__iexact=perm_codename)
    user.user_permissions.add(permission)
    return JsonResponse({'message': f'Permission {perm_codename} added to user {user.email}'})


# Remove permissions from a user
@login_required
@require_POST
def remove_permission_from_user(request, user_id, perm_codename):
    user = get_object_or_404(User, id=user_id)
    permission = get_object_or_404(Permission, codename=perm_codename)
    user.user_permissions.remove(permission)
    return JsonResponse({'message': f'Permission {perm_codename} removed from user {user.email}'})


# New endpoint to verify session
@login_required
def session_check(request):
    if request.user.is_authenticated:
        return JsonResponse({'message': f'User {request.user.email} is authenticated'}, status=200)
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)


@csrf_protect
def protected_view(request):
    return HttpResponse('Protected content')

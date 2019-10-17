from django.contrib.auth.models import User

from departments.models import Department


def add_if_not_present(username: str = None, email: str = None, first_name: str = None, last_name: str = None) -> User:
    user = User.objects.filter(username=username).first()
    if not user:
        user = User()
        user.username = username
        if email:
            user.email = email
        if last_name:
            user.first_name = first_name
            user.last_name = last_name
        elif ',' in username:
            names = username.split(', ')
            user.first_name = names[1]
            user.last_name = names[0]
        user.save()

        user.profile.active = False
        user.profile.save()

    return user


def save_profile(user: User, call_sign: str = None,
                 work_number: str = None, home_number: str = None, cell_number: str = None,
                 department: Department = None, active: bool = None) -> None:

    if call_sign and user.profile.call_sign != call_sign:
        user.profile.call_sign = call_sign
    if work_number and user.profile.work_number != work_number:
        user.profile.work_number = work_number
    if home_number and user.profile.home_number != home_number:
        user.profile.home_number = home_number
    if cell_number and user.profile.cell_number != cell_number:
        user.profile.cell_number = cell_number
    if department and user.profile.department != department:
        user.profile.department = department
    if active and user.profile.active != active:
        user.profile.active = active

    user.profile.save()

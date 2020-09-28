from django.contrib.auth.models import User

from departments.models import Department


def add_if_not_present(name: str = None, email: str = None, first_name: str = None, last_name: str = None) -> User:
    if ',' in name:
        names = name.split(', ')
        username = f'{names[1]}_{names[0]}'
    else:
        username = name.replace(' ', '_')
    user = User.objects.filter(username=username).first()
    if not user:
        user = User()
        if ',' in name:
            user.first_name = names[1]
            user.last_name = names[0]
            name = f'{names[1]} {names[0]}'
        user.username = username
        if email:
            user.email = email
        if last_name:
            user.last_name = last_name
        if first_name:
            user.first_name = first_name
        user.save()

        user.profile.active = False
        user.profile.name = name
        user.profile.save()

    return user


def save_profile(user: User, call_sign: str, 
                 work_number: str, home_number: str, cell_number: str,
                 department: Department, active: bool) -> None:

    # '!= None' is being used so that enpty strings can be the updated value
    # if name != None and user.profile.name != name:
    #     user.profile.name = name
    if call_sign != None and user.profile.call_sign != call_sign:
        user.profile.call_sign = call_sign
    if work_number != None and user.profile.work_number != work_number:
        user.profile.work_number = work_number
    if home_number != None and user.profile.home_number != home_number:
        user.profile.home_number = home_number
    if cell_number != None and user.profile.cell_number != cell_number:
        user.profile.cell_number = cell_number
    if department != None and user.profile.department != department:
        user.profile.department = department
    if active != None and user.profile.active != active:
        user.profile.active = active
    user.profile.save()

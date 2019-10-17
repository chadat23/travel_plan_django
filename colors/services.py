from .models import Color


def add_if_not_present(name: str) -> str:
    if not name or not isinstance(name, str):
        return

    name = name.lower().strip().title()

    if not Color.objects.filter(name=name).first():
        color = Color()
        color.name = name
        color.save()

    return name

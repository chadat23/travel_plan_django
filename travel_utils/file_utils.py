import os
from typing import List


def save_files_with_attributes(files, path: str, folder: str, name: str, start_date: str):
    print('in save thing')
    name = _generate_name(name, start_date)

    if folder:
        path = os.path.join(path, folder)

    os.makedirs(path, exist_ok=True)

    return _save_files_with_name(files, path, name)

    


def _save_files_with_name(files, path: str, name: str) -> List[str]:
    """
    Renames and saves files so that they're all named the same short of a suffix number

    :param files: the list of files to be saved
    :type files: List[FileStorage]
    :param name: the base name to be used to rename each file
    :type name: str
    :param path: the path to the folder where the files are to be saved
    :type path: str
    :return: a List[str] of file names. The names aren't absolute, the path isn't included.
    :rtype: List[str]
    """

    file_names = []

    for i, f in enumerate(files):
        ext = os.path.splitext(f.name)[1]
        print(ext, 'ext')
        print(dir(f))
        print(f.__dict__)
        file_name = f'{name}_{i + 1}{ext}'
        full_path = os.path.join(path, file_name)
        with open(full_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        file_names.append(file_name)

    return file_names


def _generate_name(name: str, start_date: str) -> str:
    """
    Makes a standardised name based on the input data.

    :param name: the name of the person leading a trip
    :type name: str
    :param start_date: the start date of a trip
    :type start_date: str
    :return: a str with the name
    :rtype: str
    """
    return start_date.replace('-', '') \
           + '_' \
           + name.strip().replace(' ', '_').replace(',', '')

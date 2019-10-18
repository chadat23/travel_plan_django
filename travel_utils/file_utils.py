import os
from typing import List


def save_files_with_attributes(files, name: str, start_date: str):
    name = _generate_name(name, start_date)


def _save_files_with_name(files, name: str, path: str) -> List[str]:
    """
    Renames and saves files so that they're all named the same short of a suffix number

    :param files: the list of files to be saved
    :type files: List[FileStorage]
    :param name: the base name to be used to rename each file
    :type name: str
    :param path: the path to the folder where the files are to be saved
    :type path: str
    :return: a List[str] of file names. The names aren't absolute.
    :rtype: List[str]
    """

    file_names = []
    for i, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1]
        file_name = f'{name}_{i + 1}{ext}'
        full_path = os.path.join(path, file_name)
        file.save(full_path)
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
    return name.strip().replace(' ', '_').replace(',', '') \
           + '_' \
           + start_date.replace('-', '')

import os
from typing import List

from flask import current_app
from flask_mail import Message

from travel_plan import mail
from travel_plan.travel.travels import Travel


def email_travel(travel: Travel, files: List[str], path: str):
    """
    Emails the travel plans and files to the email list.
    It's assumed that all of the files that are to be
    attached are in the same locaiton.
    :param travel: the travel object that's being email
    :type email_list: Travel
    :param files: a list of file names for which the files are to be attached to the emails
    :type files: List[str]
    :param path: the path to the folder containing the files that are to be attached
    :type path: str
    """

    contact_list = _make_contact_list(travel)
    subject = _make_subject(travel)
    body = _make_body(travel)

    try:
        _send_mail(contact_list, [os.path.join(path, file) for file in files], subject, body)
        return True
    except Exception as e:
        print('Exception', e)
        return False


def _send_mail(contact_list: List[str], files: List[str], subject: str, body: str):
    """
    Helper function to consturct and send the email.
    :param email_list: a list of recipients' email addresses
    :type email_list: List[str]
    :param files: a list of file paths for which the files are to be attached to the emails
    :type files: List[str]
    :param subject: the intended subject of the email
    :type subject: str
    :param body: the intended body of the email
    :type body: str
    """

    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=contact_list,
                  body=body)
    for file in files:
        with current_app.open_resource(file) as fp:
            name = os.path.basename(file)
            msg.attach(name, 'text/plain', fp.read())
    mail.send(msg)
    print('Email Sent')


def _make_subject(travel: Travel) -> str:
    """
    Helper function to make the email subject from the travel object
    :param travel: the travel object
    :type travel: Travel
    :return: a str of the email subject
    :rtype: str
    """

    subject = 'Travel itinerary for : '
    for traveler in travel.travelers:
        if traveler.call_sign:
            subject += traveler.call_sign + ', '
        else:
            subject += traveler.traveler.name + ', '

    return subject[:-2]


def _make_body(travel: Travel) -> str:
    """
    Helper function to make the email body from the travel object
    :param travel: the travel object
    :type travel: Travel
    :return: a str of the email body
    :rtype: str
    """
    
    body = "Here's the travel itinerary for "
    for traveler in travel.travelers:
        if traveler.call_sign:
            body += f"{traveler.traveler.name} ({traveler.call_sign}), "
        else:
            body += f"{traveler.traveler.name}, "

    body = body[:-2] + '.'

    body += '\n Thanks'

    return body


def _make_contact_list(travel: Travel) -> List[str]:
    """
    Helper function to make the list email recipients from the travel object
    :param travel: the travel object
    :type travel: Travel
    :return: a List[str] of email recipients
    :rtype: List[str]
    """
    
    email_list = list(current_app.config['DEFAULT_EMAIL_LIST'])
    [email_list.append(e.traveler.email) for e in travel.travelers]
    [email_list.append(c.email) for c in travel.contacts]

    return email_list
from __future__ import unicode_literals

from .literals import EMAIL_SEPARATORS


def split_recipient_list(recipients, separator_list=None, separator_index=0):
    separator_list = separator_list or EMAIL_SEPARATORS

    try:
        separator = separator_list[separator_index]
    except IndexError:
        return recipients
    else:
        result = []
        for recipient in recipients:
            result.extend(recipient.split(separator))

        return split_recipient_list(
            recipients=result, separator_list=separator_list,
            separator_index=separator_index + 1
        )

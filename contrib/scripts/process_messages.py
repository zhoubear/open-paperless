#!/usr/bin/env python
import os
import optparse

import sh


APP_LIST = (
    'acls', 'appearance', 'authentication', 'cabinets', 'checkouts', 'common',
    'converter', 'django_gpg', 'document_comments', 'document_indexing',
    'document_parsing', 'document_signatures', 'document_states', 'documents',
    'dynamic_search', 'events', 'linking', 'lock_manager', 'mayan_statistics',
    'mailer', 'metadata', 'mirroring', 'motd', 'navigation', 'ocr', 'permissions',
    'rest_api', 'smart_settings', 'sources', 'storage', 'tags', 'task_manager',
    'user_management'
)

LANGUAGE_LIST = (
    'ar', 'bg', 'bs_BA', 'da', 'de_DE', 'en', 'es', 'fa', 'fr', 'hu', 'id',
    'it', 'nl_NL', 'pl', 'pt', 'pt_BR', 'ro_RO', 'ru', 'sl_SI', 'tr_TR',
    'vi_VN', 'zh_CN',
)

makemessages = sh.Command('django-admin.py')
makemessages = makemessages.bake('makemessages')

compilemessages = sh.Command('django-admin.py')
compilemessages = compilemessages.bake('compilemessages')

transifex_client = sh.Command('tx')
pull_translations = transifex_client.bake('pull')
push_translations = transifex_client.bake('push')

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'mayan')
)


def process(command, app_list, language_list):
    if command == makemessages:
        print 'Making messages'
    elif command == compilemessages:
        print 'Compiling messages'
    elif command == pull_translations:
        print 'Pulling translation files'
    elif command == push_translations:
        print 'Pushing translation files'

    if command in [compilemessages, makemessages]:
        for app in app_list:
            print 'Processing app: %s...' % app
            app_path = os.path.join(BASE_DIR, 'apps', app)
            os.chdir(app_path)
            for lang in language_list:
                print 'Doing language: %s' % lang
                command(locale=lang)
    elif command == pull_translations:
        for lang in language_list:
            print 'Doing language: %s' % lang
            command('-f', '-l', lang)
    elif command == push_translations:
        for lang in language_list:
            print 'Doing language: %s' % lang
            command('-s', '-l', lang)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option(
        '-m', '--make', help='create message sources file', dest='make',
        default=False, action='store_true'
    )
    parser.add_option(
        '-c', '--compile', help='compile message files', dest='compile',
        default=False, action='store_true'
    )
    parser.add_option(
        '-p', '--pull', help='pull translation files', dest='pull',
        default=False, action='store_true'
    )
    parser.add_option(
        '-u', '--push', help='push translation files', dest='push',
        default=False, action='store_true'
    )
    parser.add_option(
        '-a', '--app', help='specify which app to process', dest='app',
        action='store', metavar='appname'
    )
    parser.add_option(
        '-l', '--lang', help='specify which language to process', dest='lang',
        action='store', metavar='language'
    )
    (opts, args) = parser.parse_args()

    if not opts.make and not opts.compile:
        parser.print_help()

    if opts.app:
        app_list = [opts.app]
    else:
        app_list = APP_LIST

    if opts.lang:
        language_list = [opts.lang]
    else:
        language_list = LANGUAGE_LIST

    if opts.make:
        process(makemessages, app_list, language_list)
    elif opts.compile:
        process(compilemessages, app_list, language_list)
    elif opts.pull:
        process(pull_translations, app_list, language_list)
    elif opts.push:
        process(push_translations, app_list, language_list)

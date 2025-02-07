from time import sleep

from pyrogram.types import ChatPermissions
from DaisyX import LOGS
from DaisyX.functions.spamhelper import edit, TEMP_SETTINGS, extract_args, daisy, send_log

BRAIN = []

def globals_init():
    try:
        global sql, sql2
        from importlib import import_module

        sql = import_module('DaisyX.plugins.sql.gban_sql')
        sql2 = import_module('DaisyX.plugins.sql.gmute_sql')
    except Exception as e:
        sql = None
        sql2 = None
        LOGS.warn("**Unable to run GBan and GMute command, no SQL connection found**")
        raise e


globals_init()


@daisy(pattern='^.gban', compat=False)
def gban_user(client, message):
    args = extract_args(message)
    reply = message.reply_to_message
    edit(message, f'`**Whacking the pest!**`')
    if args:
        try:
            user = client.get_users(args)
        except Exception:
            edit(message, f'`**Please specify a valid user!**`')
            return
    elif reply:
        user_id = reply.from_user.id
        user = client.get_users(user_id)
    else:
        edit(message, f'`**Please specify a valid user!**`')
        return

    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return edit(message, f'`Calm down, You can't ban yourself.`')
    except BaseException:
        pass

    if user.id in BRAIN:
        return edit(
            message,
                "%1Error!%1\n%2[%3](tg://user?id=%4)%2 %1is DaisyX admin..\nSo I can't do this.%1", ['`', '**', user.first_name, user.id]),
        )

    try:
        if sql.is_gbanned(user.id):
            return edit(message, f'`{get_translation("alreadyBanned")}`')
        sql.gban(user.id)
        edit(
            message,
                '%1[%2](tg://user?id=%3)%1 (%4%3%4) %4globally banned!%4', ['**', user.first_name, user.id, '`']),
        )
        try:
            common_chats = client.get_common_chats(user.id)
            for i in common_chats:
                i.kick_member(user.id)
        except BaseException:
            pass
        sleep(1)
        send_log(('#GBAN\nUSER: [%1](tg://user?id=%2)', [user.first_name, user.id])) 
    except Exception as e:
        edit(message, ('%1Something went wrong!%1\n\n%2%3%2', ['`', '**', e]))
        return

'''
@daisy(pattern='^.(ung|gun)ban', compat=False)
def ungban_user(client, message):
    args = extract_args(message)
    reply = message.reply_to_message
    edit(message, f'`{get_translation("unbanProcess")}`')
    if args:
        try:
            user = client.get_users(args)
        except Exception:
            edit(message, f'`{get_translation("banFailUser")}`')
            return
    elif reply:
        user_id = reply.from_user.id
        user = client.get_users(user_id)
    else:
        edit(message, f'`{get_translation("banFailUser")}`')
        return

    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return edit(message, f'`{get_translation("cannotUnbanMyself")}`')
    except BaseException:
        pass

    try:
        if not sql.is_gbanned(user.id):
            return edit(message, f'`{get_translation("alreadyUnbanned")}`')
        sql.ungban(user.id)

        def find_me():
            try:
                return dialog.chat.get_member(me_id).can_restrict_members
            except BaseException:
                return False

        def find_member():
            try:
                return (dialog.chat.get_member(user.id)
                    and dialog.chat.get_member(user.id).restricted_by
                    and dialog.chat.get_member(user.id).restricted_by.id == me_id)
            except BaseException:
                return False

        try:
            dialogs = client.iter_dialogs()
            me_id = TEMP_SETTINGS['ME'].id
            chats = [
                dialog.chat
                for dialog in dialogs
                if (
                    'group' in dialog.chat.type
                    and find_me()
                    and find_member()
                )
            ]
            for chat in chats:
                chat.unban_member(user.id)
        except BaseException:
            pass
        edit(
            message,
            get_translation(
                'unbanResult', ['**', user.first_name, user.id, '`']),
        )
    except Exception as e:
        edit(message, get_translation('banError', ['`', '**', e]))
        return


@daisy(pattern='^.listgban$')
def gbanlist(message):
    users = sql.gbanned_users()
    if not users:
        return edit(message, f'`{get_translation("listEmpty")}`')
    gban_list = f'**{get_translation("gbannedUsers")}**\n'
    count = 0
    for i in users:
        count += 1
        gban_list += f'**{count} -** `{i.sender}`\n'
    return edit(message, gban_list)


@daisy(incoming=True, outgoing=False, compat=False)
def gban_check(client, message):
    if sql.is_gbanned(message.from_user.id):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            client.kick_chat_member(chat_id, user_id)
        except BaseException:
            pass

    message.continue_propagation()


@daisy(pattern='^.gmute', compat=False)
def gmute_user(client, message):
    args = extract_args(message)
    reply = message.reply_to_message
    edit(message, f'`{get_translation("muteProcess")}`')
    if len(args):
        try:
            user = client.get_users(args)
        except Exception:
            edit(message, f'`{get_translation("banFailUser")}`')
            return
    elif reply:
        user_id = reply.from_user.id
        user = client.get_users(user_id)
    else:
        edit(message, f'`{get_translation("banFailUser")}`')
        return

    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return edit(message, f'`{get_translation("cannotMuteMyself")}`')
    except BaseException:
        pass

    if user.id in BRAIN:
        return edit(
            message,
            get_translation(
                'brainError', ['`', '**', user.first_name, user.id]),
        )

    try:
        if sql2.is_gmuted(user.id):
            return edit(message, f'`{get_translation("alreadyMuted")}`')
        sql2.gmute(user.id)
        edit(
            message,
            get_translation(
                'gmuteResult', ['**', user.first_name, user.id, '`']),
        )
        try:
            common_chats = client.get_common_chats(user.id)
            for i in common_chats:
                i.restrict_member(user.id, ChatPermissions())
        except BaseException:
            pass
        sleep(1)
        send_log(get_translation('gmuteLog', [user.first_name, user.id]))
    except Exception as e:
        edit(message, get_translation('banError', ['`', '**', e]))
        return


@daisy(pattern='^.ungmute', compat=False)
def ungmute_user(client, message):
    args = extract_args(message)
    reply = message.reply_to_message
    edit(message, f'`{get_translation("unmuteProcess")}`')
    if len(args):
        try:
            user = client.get_users(args)
        except Exception:
            edit(message, f'`{get_translation("banFailUser")}`')
            return
    elif reply:
        user_id = reply.from_user.id
        user = client.get_users(user_id)
    else:
        edit(message, f'`{get_translation("banFailUser")}`')
        return

    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return edit(message, f'`{get_translation("cannotUnmuteMyself")}`')
    except BaseException:
        pass

    try:
        if not sql2.is_gmuted(user.id):
            return edit(message, f'`{get_translation("alreadyUnmuted")}`')
        sql2.ungmute(user.id)
        try:
            common_chats = client.get_common_chats(user.id)
            for i in common_chats:
                i.unban_member(user.id)
        except BaseException:
            pass
        edit(
            message,
            get_translation('unmuteResult', [
                            '**', user.first_name, user.id, '`']),
        )
    except Exception as e:
        edit(message, get_translation('banError', ['`', '**', e]))
        return


@daisy(pattern='^.listgmute$')
def gmutelist(message):
    users = sql2.gmuted_users()
    if not users:
        return edit(message, f'`{get_translation("listEmpty")}`')
    gmute_list = f'**{get_translation("gmutedUsers")}**\n'
    count = 0
    for i in users:
        count += 1
        gmute_list += f'**{count} -** `{i.sender}`\n'
    return edit(message, gmute_list)


@daisy(incoming=True, outgoing=False, compat=False)
def gmute_check(client, message):
    if sql2.is_gmuted(message.from_user.id):
        sleep(0.1)
        message.delete()

        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            client.restrict_chat_member(chat_id, user_id, ChatPermissions())
        except BaseException:
            pass

    message.continue_propagation()
'''


#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import sqlite3
from pathlib import Path
from functools import wraps

script_dir = Path(__file__).parent.absolute()
#Connecting to sqlite
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
def sql_connect():
    conn = sqlite3.connect(str(script_dir) + '/rss.db')
    return conn, conn.cursor()

# Groups
def list_groups(update, context):
    conn, cursor = sql_connect()
    cursor.execute('select * from groups;')
    groups = cursor.fetchall()
    resp = ''
    counter = 0
    keyboard = [[],[],[]]
    for group in groups:
        keyboard[0].append(InlineKeyboardButton("\u2733 %s"%str(group[0]), callback_data='group_list_feeds ' + str(group[0])))
        keyboard[1].append(InlineKeyboardButton("\u2747 %s"%str(group[0]), callback_data='group_list_records ' + str(group[0])))
        resp += '\n' + str(group[0]) + '. ' + group[1]
        counter += 1
        if counter == 5 or groups.index(group) == len(groups) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(resp, reply_markup = reply_markup)
            resp = ''
            counter = 0
            keyboard = [[], [], []]
    conn.close()

def list_feeds_button(update, context, group_id):
    conn, cursor = sql_connect()
    cursor.execute('select * from feeds where group_id=?', (int(group_id),))
    feeds = cursor.fetchall()
    conn.close()
    resp = ''
    counter = 0
    keyboard = [[], []]
    for feed in feeds:
        keyboard[0].append(InlineKeyboardButton("\u2714 %s"%str(feed[0]), callback_data='feed_list_records ' + str(feed[0])))
        resp += '\n' + str(feed[0]) + '. ' + feed[1] + ': ' + feed[2]
        counter += 1
        if counter == 5 or feeds.index(feed) == len(feeds) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text=resp, chat_id=update.callback_query.message.chat.id, reply_markup=reply_markup)
            keyboard = [[], []]
            resp = ''
            counter = 0

def list_records_by_group_button(update, context, group_id):
    conn, cursor = sql_connect()
    cursor.execute('select * from records where feed_id in (select id from feeds where group_id=?)', (int(group_id),))
    records = cursor.fetchall()
    conn.close()
    resp = ''
    counter = 0
    keyboard = [[]]
    for record in records:
        keyboard[0].append(InlineKeyboardButton("\u26D4 %s"%str(record[0]), callback_data='delete_record ' + str(record[0])))
        resp += '\n' + str(record[0]) + '. ' + record[1] + ' (' + record[2] + ') '
        counter += 1
        if counter == 5 or records.index(record) == len(records) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text=resp, chat_id=update.callback_query.message.chat.id, reply_markup=reply_markup)
            keyboard = [[]]
            resp = ''
            counter = 0

# Feeds
def list_feed(update, context):
    conn, cursor = sql_connect()
    cursor.execute('select * from feeds;')
    feeds = cursor.fetchall()
    resp = ''
    counter = 0
    keyboard = [[],[]]
    for feed in feeds:
        keyboard[0].append(InlineKeyboardButton("\u2714 %s"%str(feed[0]), callback_data='feed_list_records ' + str(feed[0])))
        resp += '\n' + str(feed[0]) + '. ' + feed[1] + ': ' + feed[2]
        counter += 1
        if counter == 5 or feeds.index(feed) == len(feeds) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(resp, reply_markup=reply_markup)
            keyboard = [[], []]
            resp = ''
            counter = 0
    #update.message.reply_text(resp)
    conn.close()

def delete_feed(update, context):
    conn, cursor = sql_connect()
    if len(context.args):
        cursor.execute('delete from records where feed_id=?', (context.args[0]))
        cursos.execute('delete from feeds where id=?', (context.args[0]))
        update.message.reply_text('The feed %s was deleted'%(context.args[0]))
        conn.commit()
        conn.close()

def list_records_button(update: Update, context, feed_id):
    conn, cursor = sql_connect()
    cursor.execute('select * from records where feed_id=?', (int(feed_id),))
    records = cursor.fetchall()
    resp = ''
    counter = 0
    keyboard = [[]]
    for record in records:
        keyboard[0].append(InlineKeyboardButton("\u26D4 %s"%str(record[0]), callback_data='delete_record ' + str(record[0])))
        resp += '\n' + str(record[0]) + '. ' + record[1] + ' (' + record[2] + ') '
        counter += 1
        if counter == 5 or records.index(record) == len(records) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text=resp, chat_id=update.callback_query.message.chat.id, reply_markup=reply_markup)
            keyboard = [[]]
            resp = ''
            counter = 0
    conn.close()

# Records
def list_record(update, context):
    conn, cursor = sql_connect()
    if len(context.args):
        feed_id = context.args[0]
        cursor.execute('select * from records where feed_id=?', (int(feed_id),))
    else:
        cursor.execute('select * from records;')
    records = cursor.fetchall()
    resp = ''
    counter = 0
    keyboard = [[]]
    for record in records:
        keyboard[0].append(InlineKeyboardButton("\u26D4 %s"%str(record[0]), callback_data='delete_record ' + str(record[0])))
        counter += 1
        resp += '\n' + str(record[0]) + '. ' + record[1] + '(' + record[2] + ') ' + str(record[3])
        if counter == 5 or records.index(record) == len(records) - 1:
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(resp, reply_markup=reply_markup)
            keyboard = [[]]
            resp = ''
            counter = 0
    conn.close()

def delete_record(update, context):
    conn, cursor = sql_connect()
    if len(context.args):
        cursor.execute('delete from records where id=?', (context.args[0]))
        update.message.reply_text('The record %s was deleted'%(context.args[0]))
        conn.commit()
        conn.close()

def delete_record_button(record_id):
    conn, cursor = sql_connect()
    cursor.execute('delete from records where id=?', (int(record_id),))
    conn.commit()
    conn.close()

def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    text = query.message.reply_markup.inline_keyboard[0][0].text
    data = query.data
    cmd = data.split(' ')[0]
    data = data.split(' ')[1]
    if cmd == 'feed_list_records':
        list_records_button(update, context, data)
    elif cmd == 'delete_record':
        delete_record_button(data)
    elif cmd == 'group_list_feeds':
        list_feeds_button(update, context, data)
    elif cmd == 'group_list_records':
        list_records_by_group_button(update, context, data)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(<bot token>, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("groups", list_groups, Filters.user(user_id=<tg_user_id>)))
    dp.add_handler(CommandHandler("feeds", list_feed, Filters.user(user_id=<tg_user_id>)))
    dp.add_handler(CommandHandler("records", list_record, Filters.user(user_id=<tg_user_id>)))
    dp.add_handler(CommandHandler("delete_record", delete_record, Filters.user(user_id=<tg_user_id>)))
    dp.add_handler(CommandHandler("delete_feed", delete_feed, Filters.user(user_id=<tg_user_id>)))
    dp.add_handler(CallbackQueryHandler(callback_handler))
    # on noncommand i.e message - echo the message on Telegram
    # log all errors
    dp.add_error_handler(error)
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

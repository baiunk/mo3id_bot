# استدعاء المكتبات
# importing libraries
from datetime import datetime
import logging, datetime
from telethon.sync import TelegramClient
from telethon import events, Button
import countdown as count
import constants as c
import json
from telethon.tl import functions

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# الثوابت
# constants
token = c.token
api_id = c.api_id
api_hash = c.api_hash
bot = TelegramClient('mo3id', api_id, api_hash).start(bot_token=token)
main_devid = c.main_dev


# حدث وصول رسالة
# message event
@bot.on(events.NewMessage)
async def event_handler(event):
    # تعريف المتغيرات
    # message vars
    sender_id = event.sender_id
    chat_id = event.chat_id
    text = event.raw_text
    # أمر التشغيل
    # starting command
    if text == "/start" or text == "/start@mo3id_bot":
        # تخزين المحادثة الجديدة في الملف
        # storing chat id into data.json
        with open("data.json", "r") as f:
            datafile = json.loads(f.read())
        # إذا كان بالخاص وغير مسجل من قبل في القائمة
        # if in private and isn't in data.json
        if not str(chat_id) in list(datafile) and chat_id==sender_id:
            datafile[f"{sender_id}"]={"doing":"start", "dates":[]}
            await bot.send_message(chat_id,"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")],[Button.inline("أضفني إلى المجموعة", "https://t.me/mo3id_bot?startgroup=botstart")], [Button.inline("المصدر", "source")]])
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            return
        # يمكن للمطور فقط تفعيل البوت في المجموعات لتجنب الضغط
        # only main dev can start bot in groups
        if not str(chat_id) in list(datafile) and main_devid==sender_id and chat_id!=sender_id:
            datafile[f"{chat_id}"]={"controller":{"id":0, "doing":"start"}, "dates":[]}
            await event.reply("تم التفعيل")
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            return
        # إذا كانت المحادثة مسجلة من قبل
        # if chat already in data.json
        if str(chat_id) in list(datafile) and chat_id == sender_id:
            datafile[f"{chat_id}"]["doing"] = "start"
            await bot.send_message(chat_id,"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")],[Button.url("أضفني إلى المجموعة", "https://t.me/mo3id_bot?startgroup=botstart")], [Button.inline("المصدر", "source")]])
        if str(chat_id) in list(datafile) and chat_id != sender_id:
            sender = await event.get_sender()
            sender_firstname = sender.first_name
            # التحقق من كونه مشرفًا في المجموعة
            # Checking if sender is admin in group
            result = await bot(functions.channels.GetParticipantRequest(
            channel=chat_id,
            user_id=sender_id
            ))
            if hasattr(result.participant, 'admin_rights'):
                # تسجيل ايدي المتحكم بالقائمة
                # storing the admin who control the bot
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["id"] = sender_id
                datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await bot.send_message(chat_id,f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")
            else:
                await event.reply("عذرًا يجب أن تكون مشرفًا في المجموعة") 
        # تحديث ملف البيانات
        # update data.json
        with open("data.json", "w") as f:
            json.dump(datafile, f)
        return
    # أوامر الخاص
    # private commands
    if chat_id == sender_id:
        # إضافة اسم الموعد
        # adding date name
        if json.loads(open("data.json", "r").read())[f"{chat_id}"]["doing"] == "addingdatename":
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for date in datafile[f"{chat_id}"]["dates"]:
                if date[0] == text:
                    datafile[f"{chat_id}"]["doing"] = "start"
                    await event.reply("يوجد موعد مسجل مسبقًا بهذا العنوان", buttons=[[Button.inline("العودة", "back")]])
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                else:
                    pass
            datafile[f"{chat_id}"]["dates"].append([f"{text}"])
            datafile[f"{chat_id}"]["doing"] = "addingdate"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.reply("جميل الآن ارسل التاريخ بالميلادي وفق الصيغة\n<code>YYYY/MM/DD</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
            return
        # إضافة تاريخ الموعد
        # adding date
        if json.loads(open("data.json", "r").read())[f"{chat_id}"]["doing"] == "addingdate":
            text_list = text.split("/")
            if len(text_list)==3:
                year = int(text_list[0])
                month = int(text_list[1])
                day = int(text_list[2])
                if month<1 or month>12 or day<1 or day>30:
                    await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                    return
                if datetime.datetime(year,month,day).timestamp() < event.message.date.timestamp():
                    await event.reply("مافات قد مات", buttons=[[Button.inline("العودة", "back")]])
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["doing"] = "start"
                    datafile[f"{chat_id}"]["dates"].pop()
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                else:
                    date = datetime.datetime(year,month,day)
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(year)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(month)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(day)
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    datename = json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"][len(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"])-1][0]
                    await event.reply(f"تم إضافة الموعد <code>{datename}</code> بتاريخ <code>{year}/{month}/{day}</code>\nارسل كلمة <code>موعد</code> لرؤية المواعيد", parse_mode = "HTML")
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["doing"] = "start"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    
                    return
            if len(text_list)!=3:
                await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                return
        if text!="موعد":
            await event.reply("لا أفهم ماذا تقول ارسل\n /start")
            return
    # أوامر المتحكم
    # controller commands
    if chat_id != sender_id and sender_id == json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["id"]:
        if json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["doing"] == "addingdatename":
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for date in datafile[f"{chat_id}"]["dates"]:
                if date[0] == text:
                    await event.reply("يوجد موعد مسجل مسبقًا بهذا العنوان", buttons=[[Button.inline("العودة", "back")]])
                    datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                else:
                    pass
            datafile[f"{chat_id}"]["dates"].append([f"{text}"])
            datafile[f"{chat_id}"]["controller"]["doing"] = "addingdate"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.reply("جميل الآن ارسل التاريخ بالميلادي وفق الصيغة\n<code>YYYY/MM/DD</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
            return
        if json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["doing"] == "addingdate":
            text_list = text.split("/")
            if len(text_list)==3:
                year = int(text_list[0])
                month = int(text_list[1])
                day = int(text_list[2])
                if month<1 or month>12 or day<1 or day>30:
                    await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                    return
                if datetime.datetime(year,month,day).timestamp() < event.message.date.timestamp():
                    await event.reply("مافات قد مات", buttons=[[Button.inline("العودة", "back")]])
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                    datafile[f"{chat_id}"]["dates"].pop()
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                else:
                    date = datetime.datetime(year,month,day)
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(year)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(month)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(day)
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    datename = json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"][len(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"])-1][0]
                    await event.reply(f"تم إضافة الموعد <code>{datename}</code> بتاريخ <code>{year}/{month}/{day}</code>\nارسل كلمة <code>موعد</code> لرؤية المواعيد", parse_mode = "HTML")
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    
                    return
            if len(text_list)!=3:
                await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                return
    # عرض جميع المواعيد
    # display all dates
    if text == "موعد":
        response = ""
        with open("data.json", "r") as f:
            datafile = json.loads(f.read())
        for date in datafile[f"{chat_id}"]["dates"]:
            response += f"{count.fullcount(event,datetime.datetime(int(date[1]),int(date[2]),int(date[3])), date[0])}\n"
        response += "سبحان الله وبحمده سبحان الله العظيم"
        await event.reply(response)
        return
    if not chat_id in list(json.loads(open("data.json", "r").read())):
        return
# عندما يضيف أحد البوت لمجموعته
# when someone add the bot to a group
@bot.on(events.ChatAction)
async def handler(event):
    chat_id = event.chat_id
    if "bot id" in event.action_message.action.users:
        await bot.send_message(chat_id,"مرحبًا أنا بوت موعد سأكون مسؤولًا عن ترتيب مواعيد المجموعة\nقم برفعي مشرفًا (لا تهم الصلاحيات) وتواصل مع المطور لتفعيل البوت @orymef_bot")

# حدث ضغط زر
# button event
@bot.on(events.CallbackQuery)
async def callbackhandler(event):
    # تعريف المتغيرات
    # callbackquery vars
    sender_id = event.sender_id
    chat_id = event.chat_id
    data = event.data.decode("utf-8")
    # أوامر الخاص
    # in private
    if chat_id==sender_id:
        if data == "addingdate":
            # تخزين أوامر المتحكم
            # sorting controller commands
            with open("data.json") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["doing"] = "addingdatename"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.edit("حسنًا ارسل اسم الموعد الذي تريد إضافته", buttons=[[Button.inline("العودة","back")]], parse_mode = "HTML")
            return
        # مواعيدي
        # browsing dates
        if data == "browsedates":
            dateskey = []
            sender = await event.get_sender()
            sender_firstname = sender.first_name
            with open("data.json") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["doing"] = "browsedates"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for date in datafile[f"{chat_id}"]["dates"]:
                dateskey.append([Button.inline(f"{date[0]}", f"browse/{chat_id}:{date[0]}"), Button.inline("❌", f"del/{chat_id}:{date[0]}")])
            dateskey.append([Button.inline("العودة", "back")])
            await event.edit(f"جميع المواعيد\nقم بالضغط على عنوان الموعد لاستعراض تاريخه", buttons = dateskey, parse_mode = "HTML")
            return
        # العودة
        # back
        if data == "back":
            with open("data.json") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["doing"] = "start"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            sender = await event.get_sender()
            sender_firstname=sender.first_name
            await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")
            return
        # مصدر البوت
        # source
        if data == "source":
            with open("data.json") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["doing"] = "source"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.edit("للتواصل بشأن أي اقتراح أو تعديل t.me/orymef_bot\nللإطلاع على الأسطر البرمجية تفضل بزيارة: github.com/baiunk/mo3id_bot", buttons=[[Button.inline("العودة","back")]] )
            return
        # حذف موعد
        # deleting a date
        if f"del/{chat_id}" in data:
            datename = data.split(":", 1)[1]
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for date in datafile[f"{chat_id}"]["dates"]:
                if date[0] == datename:
                    datafile[f"{chat_id}"]["dates"].remove(date)
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.edit(f"تم مسح موعد <code>{datename}</code>", buttons=[[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
            return
        # عرض موعد
        # viewing a date
        if f"browse/{chat_id}" in data:
            datename = data.split(":", 1)[1]
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for date in datafile[f"{chat_id}"]["dates"]:
                if date[0] == datename:
                    year = date[1]
                    month = date[2]
                    day = date[3]
            await event.edit(f"موعد <code>{datename}</code> يُعقد في (<code>{year}/{month}/{day}</code>)",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
            return
        if data == "cancel":
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["dates"].pop()
            with open("data.json", "w") as f:
                json.dump(datafile,f)
            sender = await event.get_sender()
            sender_firstname=sender.first_name
            await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")

    # أوامر المجموعة
    # in group
    if chat_id!=sender_id:
        if json.loads(open("data.json").read())[f"{chat_id}"]["controller"]["id"] == sender_id:
            # إضافة موعد
            # adding a date
            if data == "addingdate":
                # تخزين أوامر المتحكم
                # sorting controller commands
                with open("data.json") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["doing"] = "addingdatename"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await event.edit("حسنًا ارسل اسم الموعد الذي تريد إضافته", buttons=[[Button.inline("العودة","back")]], parse_mode = "HTML")
                return
            # مواعيدي
            # browsing dates
            if data == "browsedates":
                dateskey = []
                sender = await event.get_sender()
                sender_firstname = sender.first_name
                with open("data.json") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["doing"] = "browsedates"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                for date in datafile[f"{chat_id}"]["dates"]:
                    dateskey.append([Button.inline(f"{date[0]}", f"browse/{chat_id}:{date[0]}"), Button.inline("❌", f"del/{chat_id}:{date[0]}")])
                dateskey.append([Button.inline("العودة", "back")])
                await event.edit(f"جميع المواعيد\nقم بالضغط على عنوان الموعد لاستعراض تاريخه\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = dateskey, parse_mode = "HTML")
                return
            # العودة
            # back
            if data == "back":
                with open("data.json") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                sender = await event.get_sender()
                sender_firstname=sender.first_name
                await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")
                return
            # مصدر البوت
            # source
            if data == "source":
                with open("data.json") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["doing"] = "source"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await event.edit("للتواصل بشأن أي اقتراح أو تعديل t.me/orymef_bot\nللإطلاع على الأسطر البرمجية تفضل بزيارة: github.com/baiunk/mo3id_bot", buttons=[[Button.inline("العودة","back")]] )
                return
            # حذف موعد
            # deleting a date
            if f"del/{chat_id}" in data:
                datename = data.split(":", 1)[1]
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                for date in datafile[f"{chat_id}"]["dates"]:
                    if date[0] == datename:
                        datafile[f"{chat_id}"]["dates"].remove(date)
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await event.edit(f"تم مسح موعد<code>{datename}</code>", buttons=[[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
                return
            # عرض موعد
            # viewing a date
            if f"browse/{chat_id}" in data:
                datename = data.split(":", 1)[1]
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                for date in datafile[f"{chat_id}"]["dates"]:
                    if date[0] == datename:
                        year = date[1]
                        month = date[2]
                        day = date[3]
                await event.edit(f"موعد <code>{datename}</code> يُعقد في (<code>{year}/{month}/{day}</code>)",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
                return
            # إلغاء تسجيل الموعد
            # canceling date
            if data == "cancel":
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["dates"].pop()
                with open("data.json", "w") as f:
                    json.dump(datafile,f)
                sender = await event.get_sender()
                sender_firstname=sender.first_name
                await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")

 

# التشغيل
# starting
bot.start()
bot.run_until_disconnected()

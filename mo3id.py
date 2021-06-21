# استدعاء المكتبات
# importing libraries
from math import floor
from datetime import datetime, tzinfo, timezone
import logging, datetime , re , pytz , json
from ummalqura.hijri_date import HijriDate
from telethon.client import buttons
from telethon.sync import TelegramClient
from telethon import events, Button
import countdown as count
import constants as c
from telethon.tl import functions

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


# الثوابت
# constants
token = c.token
api_id = c.api_id
api_hash = c.api_hash
bot = TelegramClient('session', api_id, api_hash).start(bot_token=token)
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
    if text == "/start" or text == "/start@mo3id_bot" or text == "المواعيد":
        # تخزين المحادثة الجديدة في الملف
        # storing chat id into data.json
        with open("data.json", "r") as f:
            datafile = json.loads(f.read())
        # إذا كان بالخاص وغير مسجل من قبل في القائمة
        # if in private and isn't in data.json
        if not str(chat_id) in list(datafile) and chat_id==sender_id:
            datafile[f"{sender_id}"]={"doing":"start", "dates":[]}
            await bot.send_message(chat_id,"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")],[Button.url("أضفني إلى المجموعة", "https://t.me/mo3id_bot?startgroup=botstart")], [Button.inline("المصدر", "source")]])
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            return
        # يمكن للمطور فقط تفعيل البوت في المجموعات لتجنب الضغط
        # only main dev can activate bot in groups
        if not str(chat_id) in list(datafile) and main_devid==sender_id and chat_id!=sender_id:
            datafile[f"{chat_id}"]={"controller":{"id":0, "doing":"start"}, "dates":[], "limit":10}
            await event.reply("تم التفعيل")
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            return
        # إذا كانت المحادثة مسجلة من قبل
        # if chat already in data.json
        if str(chat_id) in list(datafile) and chat_id == sender_id:
            datafile[f"{chat_id}"]["doing"] = "start"
            await bot.send_message(chat_id,"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")],[Button.url("أضفني إلى المجموعة", "https://t.me/mo3id_bot?startgroup=botstart")], [Button.inline("المصدر", "source")]])
            return
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
    # عرض جميع المواعيد
    # display all dates
    if text == "موعد":
        response = ""
        with open("data.json", "r") as f:
            datafile = json.loads(f.read())
        for date in datafile[f"{chat_id}"]["dates"]:
            response += f"{count.fullcount(datetime.datetime(int(date[1]),int(date[2]),int(date[3])), date[0])}\n"
        response += "سبحان الله وبحمده سبحان الله العظيم"
        await event.reply(response, parse_mode = "HTML")
        return
    # أوامر المطور
    # dev commands
    if sender_id == main_devid:
        text_list = text.split(" ")
        # المغادرة
        # leave command
        if text == "غادر" and sender_id != chat_id:
            await event.reply("سيعلم الجمعُ ممن ضمَّ مجلسنا , بأنني خيرُ من تسعى به قدمُ")
            await bot.delete_dialog(chat_id, revoke=True)
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            for group in list(datafile):
                if group == str(chat_id):
                    del datafile[f"{chat_id}"]
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            return
        # تعديل أقصى حد للمواعيد
        # change dates limit
        if text_list[0] == "تعديل" and text_list[1] == "الحد":
            newlimit = text_list[2]
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            oldlimit = datafile[f"{chat_id}"]["limit"]
            datafile[f"{chat_id}"]["limit"] = newlimit
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.reply(f"تم تعديل الحد من {oldlimit} إلى {newlimit}")
            return
        # لعرض أقصى حد من المواعيد في المجموعة
        # to display the limit
        if text == "الحد" and sender_id != chat_id:
            limit = json.loads(open("data.json","r").read())[f"{chat_id}"]["limit"]
            await event.reply(f"حد هذه المجموعة {limit}")
        
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
            if len(text) > 30:
                await event.reply("عذرًا اسم الموعد طويل جدًا حاول اختصاره", buttons=[[Button.inline("العودة", "back")]])
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                return
            else:
                pass
            datafile[f"{chat_id}"]["dates"].append([f"{text}"])
            datafile[f"{chat_id}"]["doing"] = "datetype"
            with open("data.json", "w") as f:
                json.dump(datafile, f)
            await event.reply("ممتاز الآن اختر نوع التاريخ (<code>هجري/ميلادي</code>)", buttons=[[Button.inline("ميلادي","datetypegr"),Button.inline("هجري","datetypehj")],[Button.inline("إلغاء", "cancel")]],parse_mode= "HTML")
            return
        # إضافة تاريخ الموعد
        # adding date
        if json.loads(open("data.json", "r").read())[f"{chat_id}"]["doing"] == "addingdate":
            dtype = json.loads(open("data.json", "r").read())[f"{chat_id}"]["dtype"]
            text_list = text.split("/")
            if len(text_list)==3:
                year = int(text_list[0])
                month = int(text_list[1])
                day = int(text_list[2])
                # التحقق من صلاحية التاريخ
                # checking the date availability
                if month<1 or month>12 or day<1 or day>30:
                    await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                    return
                # نوع التقويم
                # date calendar
                if dtype == "hj":
                    if len(str(month)) == 1:
                        month = f"0{month}"
                    if len(str(day)) == 1:
                        day = f"0{day}"
                    if HijriDate.get_georing_date(f"{year}-{month}-{day}") <= datetime.date.today():
                        with open("data.json", "r") as f:
                            datafile = json.loads(f.read())
                        datafile[f"{chat_id}"]["doing"] = "start"
                        datafile[f"{chat_id}"]["dates"].pop()
                        with open("data.json", "w") as f:
                            json.dump(datafile, f)
                        await event.reply("مافات قد مات", buttons=[[Button.inline("العودة", "back")]])
                        return
                    else:
                        if len(str(month)) == 1:
                            month = f"0{month}"
                        if len(str(day)) == 1:
                            day = f"0{day}"
                        date = HijriDate.get_georing_date(f"{year}-{month}-{day}")
                        pass
                if dtype == "gr":
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
                        pass
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.year)
                datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.month)
                datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.day)
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                datename = json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"][len(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"])-1][0]
                await event.reply(f"تم إضافة الموعد <code>{datename}</code> بتاريخ <code>{year}/{month}/{day}</code>\nأرسل عنوان الموعد لرؤية ماتبقى عليه\nأو أرسل كلمة <code>موعد</code> لرؤية جميع المواعيد",buttons = [[Button.inline("العودة", "back")]], parse_mode = "HTML")
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["doing"] = "start"
                datafile[f"{chat_id}"].pop("dtype")
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                return
            if len(text_list)!=3:
                await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                return
        # الرد على عنوان الموعد
        # reply to date name
        if len(text) <= 30:
            for response in list(json.loads(open("data.json","r").read())[f"{chat_id}"]["dates"]):
                if text == response[0]:
                    await event.reply(f"{count.fullcount(datetime.datetime(int(response[1]),int(response[2]),int(response[3])), response[0])}\nاستغفرالله", parse_mode = "HTML")
                    return
        # أمر الآن
        # now command
        if text == "الآن":
            rdtimezone = pytz.timezone('Asia/Riyadh')
            now = datetime.datetime.now(rdtimezone)
            if now.hour<=12 and now.hour != 0:
                nowtime = f"{now.hour}:{now.minute} ص"
            if now.hour >12 and now.hour != 0:
                nowtime = f"{now.hour%12}:{now.minute} م"
            if now.hour == 0:
                nowtime = f"12:{now.minute} ص"
            hijrid = HijriDate(now.year,now.month,now.day, gr=True)
            ar_day = hijrid.day_name
            await event.reply(f"الآن الوقت بتوقيت الرياض:\n<code>{nowtime}</code>\n\nاليوم <code>{ar_day}</code> بتاريخ:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{now.year}/{now.month}/{now.day} مـ</code>\n⏰", parse_mode = "HTML")
            return
        # إذا لم تكن الرسالة (موعد) سيرسل تنبيه بأن الأمر غير واضح
        # If message isn't (موعد) it will notify the user
        if text:
            await event.reply("لا أفهم ماذا تقول أرسل\n /start")
            return
    # أوامر المجموعة
    # group commands commands
    if chat_id != sender_id:
        if sender_id == json.loads(open("data.json","r").read())[f"{chat_id}"]["controller"]["id"]:
            if json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["doing"] == "addingdatename":
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                # التحقق من عدم تواجد اسم العنوان من قبل
                # checking if the date name already exists
                for date in datafile[f"{chat_id}"]["dates"]:
                    if date[0] == text:
                        await event.reply("يوجد موعد مسجل مسبقًا بهذا العنوان", buttons=[[Button.inline("العودة", "back")]])
                        datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                        with open("data.json", "w") as f:
                            json.dump(datafile, f)
                        return
                    else:
                        pass
                if len(text) > 30:
                    await event.reply("عذرًا اسم الموعد طويل جدًا حاول اختصاره", buttons=[[Button.inline("العودة", "back")]])
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                else:
                    pass
                datafile[f"{chat_id}"]["dates"].append([f"{text}"])
                datafile[f"{chat_id}"]["controller"]["doing"] = "datetype"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await event.reply("ممتاز الآن اختر نوع التاريخ (<code>هجري/ميلادي</code>)", buttons=[[Button.inline("ميلادي","datetypegr"),Button.inline("هجري","datetypehj")],[Button.inline("إلغاء", "cancel")]],parse_mode= "HTML")
                return
            # إضافة التاريخ للموعد
            # adding date
            if json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["doing"] == "addingdate":
                dtype = json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["dtype"]
                text_list = text.split("/")
                if len(text_list)==3:
                    year = int(text_list[0])
                    month = int(text_list[1])
                    day = int(text_list[2])
                    # التحقق من صلاحية التاريخ
                    # checking the date availability
                    if month<1 or month>12 or day<1 or day>30:
                        await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                        return
                    # نوع التقويم
                    # date calendar
                    if dtype == "hj":
                        if len(str(month)) == 1:
                            month = f"0{month}"
                        if len(str(day)) == 1:
                            day = f"0{day}"
                        if HijriDate.get_georing_date(f"{year}-{month}-{day}") < datetime.date.today():
                            with open("data.json", "r") as f:
                                datafile = json.loads(f.read())
                            datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                            datafile[f"{chat_id}"]["dates"].pop()
                            with open("data.json", "w") as f:
                                json.dump(datafile, f)
                            await event.reply("مافات قد مات", buttons=[[Button.inline("العودة", "back")]])
                            return
                        else:
                            if len(str(month)) == 1:
                                month = f"0{month}"
                            if len(str(day)) == 1:
                                day = f"0{day}"
                            date = HijriDate.get_georing_date(f"{year}-{month}-{day}")
                            pass
                    if dtype == "gr":
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
                            pass
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.year)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.month)
                    datafile[f"{chat_id}"]["dates"][len(datafile[f"{chat_id}"]["dates"])-1].append(date.day)
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    datename = json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"][len(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"])-1][0]
                    await event.reply(f"تم إضافة الموعد <code>{datename}</code> بتاريخ <code>{year}/{month}/{day}</code>\nأرسل عنوان الموعد لرؤية ماتبقى عليه\nأو أرسل كلمة <code>موعد</code> لرؤية جميع المواعيد",buttons = [[Button.inline("العودة", "back")]], parse_mode = "HTML")
                    with open("data.json", "r") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    return
                if len(text_list)!=3:
                    await event.reply("عذرًا الصيغة غير صحيحة\nحاول مرةً أخرى")
                    return
            # الرد على اسم الموعد
            # reply to date name
        if len(text) <= 30:
            for response in list(json.loads(open("data.json","r").read())[f"{chat_id}"]["dates"]):
                if text == response[0]:
                    await event.reply(f"{count.fullcount(datetime.datetime(int(response[1]),int(response[2]),int(response[3])), response[0])}\nاستغفرالله", parse_mode = "HTML")
                    return
        # أمر الآن
        # now command
        if text == "الآن":
            rdtimezone = pytz.timezone('Asia/Riyadh')
            now = datetime.datetime.now(rdtimezone)
            if now.hour<=12 and now.hour != 0:
                nowtime = f"{now.hour}:{now.minute} ص"
            if now.hour >12 and now.hour != 0:
                nowtime = f"{now.hour%12}:{now.minute} م"
            if now.hour == 0:
                nowtime = f"12:{now.minute} ص"
            hijrid = HijriDate(now.year,now.month,now.day, gr=True)
            ar_day = hijrid.day_name
            await event.reply(f"الآن الوقت بتوقيت الرياض:\n<code>{nowtime}</code>\n\nاليوم <code>{ar_day}</code> بتاريخ:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{now.year}/{now.month}/{now.day} مـ</code>\n⏰", parse_mode = "HTML")
            return
# حدث إضافة إلى مجموعة
# adding bot to group
@bot.on(events.ChatAction)
async def handler(event):
    chat_id = event.chat_id
    if bot id in event.action_message.action.users:
        await bot.send_message(chat_id,"السلام عليكم ورحمة الله وبركاته\nأنا بوت موعد سأكون مسؤولًا عن ترتيب مواعيد المجموعة\nقم برفعي مشرفًا (لا تهم الصلاحيات) وتواصل مع المطور لتفعيل البوت @orymef_bot")

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
        # إضافة موعد
        # adding a date
        if data == "addingdate":
            # التحقق من عدد المواعيد
            # checking dates number
            if len(list(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"]))<10:
                with open("data.json") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["doing"] = "addingdatename"
                with open("data.json", "w") as f:
                    json.dump(datafile, f)
                await event.edit("حسنًا أرسل اسم الموعد الذي تريد إضافته", buttons=[[Button.inline("العودة","back")]], parse_mode = "HTML")
                return
            if len(list(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"]))==10:
                await event.edit("تأتي وتطلب مني تسجيل أكثر من 10 مواعيد، لكنك لا تطلب باحترام، ولا تعرض علي صداقتك، أنت لم تفكر بأن تناديني <b>بموعد</b>، مالذي فعلته لك لاستحق عدم احترامك؟", parse_mode="HTML", buttons=[[Button.inline("العودة", "back")]])
                return
        # اختيار تقويم الموعد
        # choosing date calender
        if "datetype" in data:
            dtype = data[8:]
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["dtype"] = f"{dtype}"
            datafile[f"{chat_id}"]["doing"] = "addingdate"
            with open("data.json", "w") as f:
                json.dump(datafile,f)
            if dtype == "hj":
                await event.edit("جميل الآن أرسل التاريخ بالهجري وفق الصيغة\n<code>سنة/شهر/يوم</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
            if dtype == "gr":
                await event.edit("جميل الآن أرسل التاريخ بالميلادي وفق الصيغة\n<code>YYYY/MM/DD</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
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
            await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")],[Button.url("أضفني إلى المجموعة", "https://t.me/mo3id_bot?startgroup=botstart")], [Button.inline("المصدر", "source")]], parse_mode="HTML")
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
                    year = int(date[1])
                    month = int(date[2])
                    day = int(date[3])
                    hijrid = HijriDate(year,month,day, gr=True)
                    ar_day = hijrid.day_name
                    rdtimezone = pytz.timezone('Asia/Riyadh')
                    datetimestamped = datetime.datetime(year,month,day).timestamp()-datetime.datetime.now(rdtimezone).timestamp()
                    days = count.countdown(datetimestamped)
                    hours = count.hours_countdown(datetimestamped)
                    minutes = count.min_countdown(datetimestamped)
                    seconds = count.sec_countdown(floor(datetimestamped%60))
                    until = ""
                    if datetimestamped>=0:
                        until = f"{days}\n{hours}\n{minutes}\n{seconds}"
                        await event.edit(f"موعد <code>{datename}</code> يُعقد في يوم <code>{ar_day}</code> الموافق:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{year}/{month}/{day} مـ</code>\nويبقى عليه ⏰:\n{until}\nلا إله إلا الله",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
                    if datetimestamped<0:
                        await event.edit(f"موعد <code>{datename}</code> انتهى في يوم <code>{ar_day}</code>\nبتاريخ:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{year}/{month}/{day} مـ</code>\nلا إله إلا الله",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
            return
        if data == "cancel":
            with open("data.json", "r") as f:
                datafile = json.loads(f.read())
            datafile[f"{chat_id}"]["dates"].pop()
            datafile[f"{chat_id}"]["doing"] = "start"
            datafile[f"{chat_id}"].pop("dtype")
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
                # التحقق من عدد المواعيد
                # checking dates number
                if len(list(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"]))<10:
                    # تخزين أوامر المتحكم
                    # sorting controller commands
                    with open("data.json") as f:
                        datafile = json.loads(f.read())
                    datafile[f"{chat_id}"]["controller"]["doing"] = "addingdatename"
                    with open("data.json", "w") as f:
                        json.dump(datafile, f)
                    await event.edit("حسنًا أرسل اسم الموعد الذي تريد إضافته", buttons=[[Button.inline("العودة","back")]], parse_mode = "HTML")
                    return
                if len(list(json.loads(open("data.json", "r").read())[f"{chat_id}"]["dates"]))==json.loads(open("data.json", "r").read())[f"{chat_id}"]["limit"]:
                    limit = json.loads(open("data.json", "r").read())[f"{chat_id}"]["limit"]
                    await event.edit(f"تأتي وتطلب مني تسجيل أكثر من {limit} مواعيد، لكنك لا تطلب باحترام، ولا تعرض علي صداقتك، أنت لم تفكر بأن تناديني <b>بموعد</b>، مالذي فعلته لك لاستحق عدم احترامك؟", parse_mode="HTML", buttons=[[Button.inline("العودة", "back")]])
                    return
            # اختيار تقويم الموعد
            # choosing date calender
            if "datetype" in data and json.loads(open("data.json", "r").read())[f"{chat_id}"]["controller"]["doing"] == "datetype":
                dtype = data[8:]
                if dtype == "hj":
                    await event.edit("جميل الآن أرسل التاريخ بالهجري وفق الصيغة\n<code>سنة/شهر/يوم</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
                if dtype == "gr":
                    await event.edit("جميل الآن أرسل التاريخ بالميلادي وفق الصيغة\n<code>YYYY/MM/DD</code>\n⏰", buttons= [[Button.inline("إلغاء", "cancel")]], parse_mode="HTML")
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["controller"]["dtype"] = f"{dtype}"
                datafile[f"{chat_id}"]["controller"]["doing"] = "addingdate"
                with open("data.json", "w") as f:
                    json.dump(datafile,f)
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
                        year = int(date[1])
                        month = int(date[2])
                        day = int(date[3])
                        # المنطقة الزمنية
                        # timezone
                        hijrid = HijriDate(year,month,day, gr=True)
                        ar_day = hijrid.day_name
                        rdtimezone = pytz.timezone('Asia/Riyadh')
                        datetimestamped = datetime.datetime(year,month,day).timestamp()-datetime.datetime.now(rdtimezone).timestamp()
                        days = count.countdown(datetimestamped)
                        hours = count.hours_countdown(datetimestamped)
                        minutes = count.min_countdown(datetimestamped)
                        seconds = count.sec_countdown(floor(datetimestamped%60))
                        until = ""
                        if datetimestamped>=0:
                            until = f"{days}\n{hours}\n{minutes}\n{seconds}"
                            await event.edit(f"موعد <code>{datename}</code> يُعقد في يوم <code>{ar_day}</code> الموافق:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{year}/{month}/{day} مـ</code>\nويبقى عليه ⏰:\n{until}\nلا إله إلا الله",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
                        if datetimestamped<0:
                            await event.edit(f"موعد <code>{datename}</code> انتهى في يوم <code>{ar_day}</code>\nبتاريخ:\n<code>{hijrid.year}/{hijrid.month}/{hijrid.day} هـ</code>\n<code>{year}/{month}/{day} مـ</code>\nلا إله إلا الله",buttons = [[Button.inline("العودة", "browsedates")]],parse_mode = "HTML")
                return
            # إلغاء تسجيل الموعد
            # canceling date
            if data == "cancel":
                with open("data.json", "r") as f:
                    datafile = json.loads(f.read())
                datafile[f"{chat_id}"]["dates"].pop()
                datafile[f"{chat_id}"]["controller"]["doing"] = "start"
                with open("data.json", "w") as f:
                    json.dump(datafile,f)
                sender = await event.get_sender()
                sender_firstname=sender.first_name
                await event.edit(f"أهلًا بك في بوت موعد\nاستخدم الازرار بالأسفل للتحكم بالبوت\nيتم التحكم في القائمة بواسطة: <code>{sender_firstname}</code>", buttons = [[Button.inline("إضافة موعد", "addingdate"), Button.inline("مواعيدي", "browsedates")], [Button.inline("المصدر", "source")]], parse_mode="HTML")

 

# التشغيل
# starting
bot.start()
bot.run_until_disconnected()

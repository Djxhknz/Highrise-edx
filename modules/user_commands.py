"""
أوامر المستخدمين العامة
"""
import asyncio
import time
import random
from highrise import Position

class UserCommands:
    def __init__(self, bot):
        self.bot = bot
        print("👤 أوامر المستخدمين جاهزة")

    async def handle_command(self, user, message: str) -> str:
        """معالجة أوامر المستخدمين"""
        try:
            # فحص الأوامر الأساسية
            if message.lower() in ["الأوامر", "commands", "help"]:
                return self.get_help_message()

            elif message.lower() in ["stop", "توقف", "قف"]:
                return await self.stop_emote(user)

            elif message.startswith("/d "):
                emote_code = message[3:].strip()
                if emote_code:
                    return await self.handle_emote_discovery(emote_code, user)

            elif message.lower() in ["ارقص", "dance", "رقص"]:
                return await self.random_dance(user)

            elif message.lower() == "موقعي":
                return await self.get_user_position(user)

            elif message.lower() in ["بوت ارقص", "bot dance"]:
                return await self.bot_dance()

            elif message.lower() in ["بوت توقف", "bot stop"]:
                return await self.bot_stop()

            # معالجة الأوامر الرقمية
            elif message.isdigit():
                return await self.handle_numeric_command(user, message)

            return None

        except Exception as e:
            print(f"خطأ في معالجة أمر المستخدم: {e}")
            return f"❌ خطأ في تنفيذ الأمر: {str(e)}"

    async def handle_numeric_command(self, user, number: str):
        """معالجة الأوامر الرقمية للرقصات"""
        try:
            emote_number = int(number)

            # التحقق من وجود مدير الرقصات
            if hasattr(self.bot, 'emotes_manager') and self.bot.emotes_manager:
                # الحصول على الرقصة بالرقم
                emote = self.bot.emotes_manager.get_emote_by_number(emote_number)

                if emote:
                    # إيقاف الرقصة الحالية إن وجدت
                    if user.id in self.bot.auto_emotes:
                        self.bot.auto_emotes[user.id]["task"].cancel()

                    # بدء الرقصة التلقائية
                    import asyncio
                    task = asyncio.create_task(self.bot.repeat_emote_for_user(user.id, emote))
                    self.bot.auto_emotes[user.id] = {"emote": emote, "task": task}

                    return f"🎭 رقصة رقم {emote_number}: {emote}\n🔄 ستتكرر تلقائياً حتى إيقافها بأمر 'توقف'"
                else:
                    return f"❌ الرقصة رقم {emote_number} غير موجودة"
            else:
                # قائمة رقصات افتراضية مرقمة
                default_emotes = [
                    "idle-loop-energetic", "emote-dance1", "emote-dance2", "emote-dance3", 
                    "dance-tiktok2", "dance-handsup", "dance-employee", "emote-maniac",
                    "idle-dance-casual", "dance-breakdance"
                ]

                if 1 <= emote_number <= len(default_emotes):
                    emote = default_emotes[emote_number - 1]

                    # إيقاف الرقصة الحالية إن وجدت
                    if user.id in self.bot.auto_emotes:
                        self.bot.auto_emotes[user.id]["task"].cancel()

                    # بدء الرقصة التلقائية
                    import asyncio
                    task = asyncio.create_task(self.bot.repeat_emote_for_user(user.id, emote))
                    self.bot.auto_emotes[user.id] = {"emote": emote, "task": task}

                    return f"🎭 رقصة رقم {emote_number}: {emote}\n🔄 ستتكرر تلقائياً حتى إيقافها بأمر 'توقف'"
                else:
                    return f"❌ الرقصة رقم {emote_number} غير متاحة (1-{len(default_emotes)})"

        except ValueError:
            return f"❌ رقم غير صحيح: {number}"
        except Exception as e:
            print(f"خطأ في معالجة الأمر الرقمي: {e}")
            return f"❌ فشل في تنفيذ الرقصة رقم {number}"

    async def handle_emote_discovery(self, emote_code: str, user):
        """معالجة اكتشاف الرقصة حسب الخطوات المطلوبة"""
        try:
            # فحص إذا كانت الرقصة موجودة في النظام
            emote_exists = False
            emote_duration = None

            # فحص في مدير التوقيت
            if hasattr(self.bot, 'emote_timing') and self.bot.emote_timing:
                emote_duration = self.bot.emote_timing.get_emote_duration(emote_code)
                # الرقصات المعروفة لها مدة محددة في النظام
                if emote_duration and emote_duration != 4.5:  # 4.5 هي القيمة الافتراضية للرقصات غير المعروفة
                    emote_exists = True

            if emote_exists:
                # الرقصة موجودة في الكود - تنفيذ مباشر
                await self.bot.highrise.send_emote(emote_code, user.id)

                # إيقاف الرقصة الحالية إن وجدت
                if user.id in self.bot.auto_emotes:
                    self.bot.auto_emotes[user.id]["task"].cancel()

                # بدء الرقصة التلقائية
                task = asyncio.create_task(self.bot.repeat_emote_for_user(user.id, emote_code))
                self.bot.auto_emotes[user.id] = {"emote": emote_code, "task": task}

                return f"🎭 تم بدء الرقصة التلقائية بالكود: {emote_code}\n🔄 ستتكرر تلقائياً حتى إيقافها بأمر 'توقف'"

            else:
                # رقصة جديدة - تطبيق الخطوات المطلوبة
                await self.bot.highrise.chat(f"🔍 اكتشاف رقصة جديدة: {emote_code}")
                await self.bot.highrise.chat(f"⏱️ جاري قياس مدة الرقصة...")

                # الخطوة 1: إرسال الرقصة مرة واحدة لقياس مدتها
                start_time = time.time()
                await self.bot.highrise.send_emote(emote_code, user.id)

                # انتظار انتهاء الرقصة لحساب مدتها (تقدير أولي)
                await asyncio.sleep(2)  # انتظار أساسي

                # قياس مدة إضافية للرقصات الطويلة
                duration = await self.calculate_emote_duration(emote_code, user.id)

                # الخطوة 2: إرسال رسالة تأكيد
                await self.bot.highrise.chat(f"✅ تم قياس مدة الرقصة: {duration} ثانية")

                # الخطوة 3: إضافة الرقصة للنظام
                await self.add_discovered_emote(emote_code, duration)

                # الخطوة 4: بدء الرقصة التلقائية
                # إيقاف الرقصة الحالية إن وجدت
                if user.id in self.bot.auto_emotes:
                    self.bot.auto_emotes[user.id]["task"].cancel()

                # بدء الرقصة التلقائية
                task = asyncio.create_task(self.bot.repeat_emote_for_user(user.id, emote_code))
                self.bot.auto_emotes[user.id] = {"emote": emote_code, "task": task}

                return f"🎉 رقصة جديدة مكتشفة وتم حفظها!\n🎭 بدء الرقصة التلقائية: {emote_code}"

        except Exception as e:
            print(f"خطأ في معالجة اكتشاف الرقصة: {e}")
            return f"❌ فشل في معالجة الرقصة: {emote_code}"

    async def calculate_emote_duration(self, emote_code: str, user_id: str) -> float:
        """حساب مدة الرقصة بطريقة تجريبية"""
        try:
            # مراقبة الرقصة لمدة أقصاها 15 ثانية
            max_watch_time = 15.0
            check_interval = 0.5  # فحص كل نصف ثانية
            start_time = time.time()

            # انتظار لانتهاء الرقصة أو انتهاء الوقت المحدد
            while time.time() - start_time < max_watch_time:
                await asyncio.sleep(check_interval)

                # فحص إذا انتهت الرقصة (هذا تقدير، يمكن تحسينه)
                current_time = time.time() - start_time

                # إذا مرت فترة معقولة، نعتبر أنها انتهت
                if current_time >= 3.0:
                    # تقدير المدة بناءً على نوع الرقصة
                    if emote_code.startswith("idle-"):
                        return min(current_time, 25.0)
                    elif emote_code.startswith("dance-"):
                        return min(current_time, 12.0)
                    elif emote_code.startswith("emote-"):
                        return min(current_time, 8.0)
                    else:
                        return min(current_time, 6.0)

            # إذا لم نستطع تحديد المدة، نعطي قيمة افتراضية
            return 6.0

        except Exception as e:
            print(f"خطأ في حساب مدة الرقصة: {e}")
            return 5.0  # قيمة افتراضية

    async def add_discovered_emote(self, emote_code: str, duration: float):
        """إضافة الرقصة المكتشفة للنظام مع إعلان الإحصائيات"""
        try:
            # إضافة إلى مدير التوقيت
            if hasattr(self.bot, 'emote_timing') and self.bot.emote_timing:
                success = self.bot.emote_timing.update_emote_duration(emote_code, duration)

                if success:
                    # حساب عدد الرقصات الجديدة المكتشفة
                    total_new_emotes = len(self.bot.emote_timing.custom_durations)

                    # إرسال رسالة تأكيد مع العدد
                    await self.bot.highrise.chat(f"💾 تم حفظ الرقصة في النظام")
                    await self.bot.highrise.chat(f"🎊 إجمالي الرقصات الجديدة المكتشفة: {total_new_emotes}")

                    print(f"✅ تم إضافة رقصة جديدة: {emote_code} = {duration}ث")
                    print(f"📊 إجمالي الرقصات الجديدة: {total_new_emotes}")
                else:
                    await self.bot.highrise.chat(f"⚠️ فشل في حفظ الرقصة، لكن سيتم استخدامها مؤقتاً")
            else:
                await self.bot.highrise.chat(f"⚠️ مدير التوقيت غير متاح، سيتم استخدام مدة افتراضية")

        except Exception as e:
            print(f"خطأ في إضافة الرقصة المكتشفة: {e}")
            await self.bot.highrise.chat(f"⚠️ حدث خطأ في حفظ الرقصة، لكن يمكن استخدامها")

    async def stop_emote(self, user):
        """إيقاف الرقصة التلقائية للمستخدم"""
        try:
            if user.id in self.bot.auto_emotes:
                # إيقاف المهمة أولاً (هذا هو الأهم)
                self.bot.auto_emotes[user.id]["task"].cancel()
                del self.bot.auto_emotes[user.id]

                # محاولة إرسال رقصة إيقاف (اختيارية)
                free_emotes = ["emote-wave", "emote-hello", "emote-thumbsup", "emote-peace", "idle-loop"]

                for emote in free_emotes:
                    try:
                        await self.bot.highrise.send_emote(emote, user.id)
                        return f"⏹️ تم إيقاف الرقصة التلقائية لـ {user.username} بنجاح"
                    except Exception as emote_error:
                        print(f"فشل في إرسال رقصة {emote}: {emote_error}")
                        continue

                # حتى لو فشلت رقصة الإيقاف، المهم أن المهمة توقفت
                return f"⏹️ تم إيقاف الرقصة التلقائية لـ {user.username} بنجاح"
            else:
                return f"ℹ️ {user.username} لا يرقص حالياً"
        except Exception as e:
            print(f"خطأ في إيقاف الرقصة: {e}")
            # فحص إذا تم حذف المهمة رغم الخطأ
            if user.id not in self.bot.auto_emotes:
                return f"⏹️ تم إيقاف الرقصة التلقائية لـ {user.username} بنجاح"
            else:
                return f"❌ فشل في إيقاف الرقصة"

    async def random_dance(self, user):
        """رقصة عشوائية للمستخدم"""
        try:
            if hasattr(self.bot, 'emotes_manager') and self.bot.emotes_manager:
                emote = self.bot.emotes_manager.get_random_emote()
                await self.bot.highrise.send_emote(emote, user.id)
                return f"💃 رقصة عشوائية: {emote}"
            else:
                # قائمة رقصات افتراضية
                emotes = ["emote-dance1", "emote-dance2", "emote-dance3", "dance-tiktok2"]
                emote = random.choice(emotes)
                await self.bot.highrise.send_emote(emote, user.id)
                return f"💃 رقصة عشوائية: {emote}"
        except Exception as e:
            print(f"خطأ في الرقصة العشوائية: {e}")
            return f"❌ فشل في تنفيذ الرقصة العشوائية"

    async def get_user_position(self, user):
        """الحصول على موقع المستخدم"""
        try:
            if hasattr(self.bot, 'location_tracker') and self.bot.location_tracker:
                location = self.bot.location_tracker.get_user_location(user.id)
                if location:
                    return f"📍 موقعك: X:{location.x:.1f}, Y:{location.y:.1f}, Z:{location.z:.1f}"
                else:
                    return "❌ لم يتم العثور على موقعك"
            else:
                return "❌ نظام تتبع المواقع غير متاح"
        except Exception as e:
            print(f"خطأ في الحصول على الموقع: {e}")
            return f"❌ فشل في الحصول على الموقع"

    async def bot_dance(self):
        """جعل البوت يرقص"""
        try:
            if hasattr(self.bot, 'emotes_manager') and self.bot.emotes_manager:
                emote = self.bot.emotes_manager.get_random_emote()
            else:
                emotes = ["emote-dance1", "emote-dance2", "emote-dance3", "dance-tiktok2"]
                emote = random.choice(emotes)

            await self.bot.highrise.send_emote(emote, self.bot.user.id)
            return f"🤖 البوت يرقص: {emote}"
        except Exception as e:
            print(f"خطأ في رقصة البوت: {e}")
            return f"❌ فشل في جعل البوت يرقص"

    async def bot_stop(self):
        """إيقاف رقصة البوت"""
        try:
            await self.bot.highrise.send_emote("idle-loop", self.bot.user.id)
            return "⏹️ تم إيقاف رقصة البوت"
        except Exception as e:
            print(f"خطأ في إيقاف البوت: {e}")
            return f"❌ فشل في إيقاف البوت"

    def get_help_message(self):
        """رسالة المساعدة"""
        return """
🤖 أوامر البوت المتاحة:

👤 أوامر المستخدمين:
• ارقص / dance - رقصة عشوائية
• توقف / stop - إيقاف الرقصة التلقائية
• موقعي - عرض موقعك الحالي
• /d [كود الرقصة] - اكتشاف رقصة جديدة

🤖 أوامر البوت:
• بوت ارقص - جعل البوت يرقص
• بوت توقف - إيقاف رقصة البوت

📋 معلومات:
• الأوامر / commands - عرض هذه الرسالة
        """
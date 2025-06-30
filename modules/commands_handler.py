"""
معالج الأوامر المركزي
"""
import os
from .user_commands import UserCommands
from .moderator_commands import ModeratorCommands
from .permission_checker import PermissionChecker

class CommandsHandler:
    def __init__(self, bot):
        self.bot = bot
        self.user_commands = UserCommands(bot)
        self.moderator_commands = ModeratorCommands(bot)
        self.permission_checker = PermissionChecker(bot.user_manager) # تهيئة مدقق الصلاحيات
        print("📝 معالج الأوامر الموحد جاهز")

    async def handle_command(self, user, message: str) -> str:
        """معالجة الأوامر مع فحص الصلاحيات"""
        try:
            print(f"🎯 معالجة أمر: {message} من {user.username}")

            # فحص الصلاحيات أولاً
            permission_result = self.permission_checker.check_command_permission(user, message)

            # إذا لم يكن مسموحاً بالأمر
            if not permission_result["allowed"]:
                print(f"🚫 تم رفض الأمر للمستخدم {user.username}: نقص صلاحيات")
                return permission_result["message"]

            # فحص أوامر المشرفين
            moderator_result = await self.moderator_commands.handle_command(user, message)
            if moderator_result:
                # إرسال الرد
                try:
                    await self.bot.highrise.chat(moderator_result)
                    print(f"💬 رد على {user.username}: {moderator_result}")
                except Exception as e:
                    print(f"❌ خطأ في إرسال الرد: {e}")
                return

            # أوامر المستخدمين
            user_result = await self.user_commands.handle_command(user, message)
            if user_result:
                return user_result

            # فحص أمر تغيير الملابس
            if message.startswith("تغيير "):
                # استخراج أكواد الملابس
                outfit_codes = message[6:].strip()  # إزالة "تغيير "
                if outfit_codes:
                    print(f"👔 بدء تغيير الزي: {outfit_codes}")
                    return await self.handle_outfit_change(outfit_codes)
                else:
                    return "❌ يرجى تحديد أكواد الملابس للتغيير"

            # فحص أوامر الرسائل العامة
            if message.startswith("رسالة ") or message.startswith("say "):
                # استخراج الرسالة
                if message.startswith("رسالة "):
                    public_message = message[6:].strip()  # إزالة "رسالة "
                else:
                    public_message = message[4:].strip()  # إزالة "say "

                if public_message:
                    # إرسال الرسالة مباشرة في الشات
                    await self.bot.highrise.chat(public_message)
                    print(f"📢 تم إرسال رسالة عامة: {public_message}")
                    return f"✅ تم إرسال الرسالة: {public_message}"
                else:
                    return "❌ يرجى كتابة رسالة للإرسال"

            # فحص الأوامر المخصصة
            try:
                # أولاً: فحص الأوامر المخصصة الجديدة (الرقص والنقل)
                from modules.custom_commands_manager import custom_commands_manager
                custom_result = await custom_commands_manager.handle_custom_command(user, message, self.bot)
                if custom_result:
                    print(f"✅ تم تنفيذ أمر مخصص: {message} للمستخدم {user.username}")
                    return custom_result

                # ثانياً: فحص أوامر التنقل من الملف المحدث
                if os.path.exists("custom_commands_config.py"):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("custom_commands_config", "custom_commands_config.py")
                    custom_config = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(custom_config)

                    is_custom, cmd_data = custom_config.is_custom_command(message)
                    if is_custom:
                        # تنفيذ أمر التنقل
                        from highrise import Position
                        coords = cmd_data.get("coordinates", {})
                        position = Position(
                            x=coords.get("x", 0),
                            y=coords.get("y", 0),
                            z=coords.get("z", 0)
                        )

                        await self.bot.highrise.teleport(user.id, position)
                        print(f"✅ تم تنفيذ أمر تنقل مخصص: {message} للمستخدم {user.username}")
                        return cmd_data.get("message", f"تم النقل إلى {cmd_data.get('command')}")

            except Exception as e:
                print(f"❌ خطأ في فحص الأوامر المخصصة: {e}")
                import traceback
                traceback.print_exc()

            # معالجة الأوامر حسب النوع
            if user_result:
                if isinstance(user_result, str):
                    # إرسال رد نصي
                    await self.bot.highrise.chat(f"💬 رد على {user.username}: {user_result}")
                elif isinstance(user_result, dict):
                    # معالجة رد معقد
                    await self.handle_complex_response(user, user_result)
            else:
                # فحص إضافي للأوامر الخاصة مثل /d
                if message.startswith("/d "):
                    emote_code = message[3:].strip()
                    if emote_code:
                        try:
                            # التحقق من صحة كود الرقصة (تجربة إرسالها أولاً)
                            await self.bot.highrise.send_emote(emote_code, user.id)

                            # إيقاف الرقصة الحالية إن وجدت
                            if user.id in self.bot.auto_emotes:
                                self.bot.auto_emotes[user.id]["task"].cancel()

                            # بدء الرقصة التلقائية
                            import asyncio
                            task = asyncio.create_task(self.bot.repeat_emote_for_user(user.id, emote_code))
                            self.bot.auto_emotes[user.id] = {"emote": emote_code, "task": task}

                            await self.bot.highrise.chat(f"💬 رد على {user.username}: 🎭 تم بدء الرقصة التلقائية بالكود: {emote_code}\n🔄 ستتكرر تلقائياً حتى إيقافها بأمر 'توقف'")
                            print(f"✅ تم تنفيذ أمر /d بنجاح: {emote_code} للمستخدم {user.username}")
                        except Exception as e:
                            await self.bot.highrise.chat(f"💬 رد على {user.username}: ❌ كود الرقصة غير صحيح أو غير متاح: {emote_code}\n🔍 تأكد من الكود وحاول مرة أخرى")
                            print(f"❌ فشل في تنفيذ أمر /d: {str(e)}")
                    else:
                        await self.bot.highrise.chat(f"💬 رد على {user.username}: ❌ يرجى كتابة كود الرقصة بعد /d\n💡 مثال: /d emote-dance1")
                else:
                    # لا يوجد رد - قد يكون أمر غير معروف أو تم تنفيذه بصمت
                    print(f"⚠️ أمر غير معروف: {message}")

            return None

        except Exception as e:
            error_msg = f"❌ خطأ في تنفيذ الأمر: {str(e)}"
            print(f"خطأ في معالجة الأمر: {e}")
            await self.bot.highrise.chat(f"💬 رد على {user.username}: {error_msg}")
            return error_msg

    async def handle_outfit_change(self, outfit_codes: str):
        """معالجة أمر تغيير الملابس"""
        try:
            from highrise import Item
            
            # تقسيم الأكواد
            codes = outfit_codes.split()
            print(f"👔 معالجة {len(codes)} قطعة ملابس")
            
            # إنشاء قائمة العناصر
            outfit_items = []
            valid_codes = []
            invalid_codes = []
            
            for code in codes:
                code = code.strip()
                if code:
                    try:
                        # التحقق من صحة الكود
                        if self.is_valid_clothing_code(code):
                            item = Item(
                                type='clothing',
                                amount=1,
                                id=code,
                                account_bound=False,
                                active_palette=-1
                            )
                            outfit_items.append(item)
                            valid_codes.append(code)
                            print(f"✅ تمت إضافة: {code}")
                        else:
                            invalid_codes.append(code)
                            print(f"❌ كود غير صحيح: {code}")
                    except Exception as e:
                        invalid_codes.append(code)
                        print(f"❌ خطأ في كود {code}: {e}")
            
            if not outfit_items:
                return f"❌ لا توجد أكواد ملابس صحيحة للتطبيق"
            
            # تطبيق الزي الجديد
            try:
                await self.bot.highrise.set_outfit(outfit=outfit_items)
                print(f"✅ تم تطبيق الزي الجديد: {len(outfit_items)} قطعة")
                
                # إرسال رسالة تأكيد
                success_msg = f"👔✨ تم تغيير زي البوت بنجاح!"
                success_msg += f"\n✅ تم تطبيق {len(valid_codes)} قطعة"
                
                if invalid_codes:
                    success_msg += f"\n⚠️ أكواد مرفوضة ({len(invalid_codes)}): {', '.join(invalid_codes[:3])}"
                    if len(invalid_codes) > 3:
                        success_msg += f" و {len(invalid_codes) - 3} أخرى"
                
                await self.bot.highrise.chat(success_msg)
                return success_msg
                
            except Exception as outfit_error:
                error_details = str(outfit_error)
                print(f"❌ فشل في تطبيق الزي: {outfit_error}")
                
                if "not owned" in error_details or "not free" in error_details:
                    return "❌ بعض قطع الملابس غير متاحة أو غير مملوكة للبوت"
                elif "Invalid item" in error_details:
                    return "❌ بعض أكواد الملابس غير صحيحة"
                else:
                    return f"❌ فشل في تطبيق الملابس: {error_details}"
                    
        except Exception as e:
            error_msg = f"❌ خطأ في معالجة تغيير الملابس: {str(e)}"
            print(error_msg)
            return error_msg

    def is_valid_clothing_code(self, item_id: str) -> bool:
        """فحص صحة كود الملابس"""
        try:
            # فحص أن الكود ليس فارغ
            if not item_id or len(item_id.strip()) == 0:
                return False

            # فحص وجود علامة - في الكود
            if '-' not in item_id:
                return False

            # فحص أن الكود لا يحتوي على أحرف غير مقبولة
            invalid_chars = [' ', '\n', '\t', '\r']
            if any(char in item_id for char in invalid_chars):
                return False

            # قائمة بأنواع الملابس المعروفة
            valid_prefixes = [
                'hair_front', 'hair_back', 'hat', 'mask', 'shirt', 'pants', 'shoes',
                'bag', 'handbag', 'watch', 'eye', 'mouth', 'body', 'face_accessory',
                'necklace', 'jacket', 'dress', 'skirt', 'top', 'bottom', 'gloves',
                'eyebrow', 'nose', 'freckle', 'glasses', 'face_hair'
            ]

            # فحص أن الكود يبدأ بنوع ملابس صحيح
            item_type = item_id.split('-')[0]
            if item_type in valid_prefixes:
                return True

            # فحص أنماط أخرى شائعة
            if item_id.startswith(('outfit-', 'clothing-', 'accessory-')):
                return True

            return False

        except Exception as e:
            print(f"خطأ في فحص كود الملابس {item_id}: {e}")
            return False
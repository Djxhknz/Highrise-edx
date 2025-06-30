
"""
نظام فحص الصلاحيات المركزي
"""

class PermissionChecker:
    def __init__(self, user_manager):
        self.user_manager = user_manager

    def check_command_permission(self, user, command: str) -> dict:
        """فحص صلاحيات الأمر"""
        username = user.username
        user_id = user.id
        
        is_owner = self.user_manager.is_owner(username)
        is_moderator = self.user_manager.is_moderator(username)
        user_type = self.user_manager.get_user_type(username, user_id)
        
        # أوامر المالك فقط
        owner_commands = [
            "اضافة_مشرف @", "ازالة_مشرف @", "احذف مكان", "promote ", "demote "
        ]
        
        # أوامر المشرفين
        moderator_commands = [
            "حفظ", "اذهب", "الاماكن", "عدد الاماكن", "اسحبهم", "جيب @",
            "بدل", "bot_dance", "رقص البوت", "تغيير", "ريأكشن",
            "المشرفين", "فحص @", "فحصني", "احصائيات_الغرفة",
            "قائمة_المشرفين", "ثبت @", "الغ ثبت @", "إلغاء_التثبيت @",
            "سجن @", "المثبتين", "ايقاف @", "رقص_الكل", "ايقاف_الكل",
            "غرفة", "حالة_الغرفة", "فحص_صلاحيات @", "مزامنة_الصلاحيات"
        ]
        
        # فحص نوع الأمر
        requires_owner = any(command.startswith(cmd) for cmd in owner_commands)
        requires_moderator = any(command.startswith(cmd) or command == cmd for cmd in moderator_commands)
        
        # النتيجة
        result = {
            "allowed": True,
            "user_type": user_type,
            "is_owner": is_owner,
            "is_moderator": is_moderator,
            "message": None
        }
        
        if requires_owner and not is_owner:
            result["allowed"] = False
            result["message"] = f"❌ المعذرة يا {username}، الأمر ده للريس بس! إنت مش صاحب البوت"
        elif requires_moderator and not is_moderator and not is_owner:
            result["allowed"] = False
            result["message"] = f"❌ آسف يا {username}، الأمر ده للمشرفين بس!\n👤 إنت: {user_type}\n💡 كلم المشرفين علشان يدوك الصلاحيات"
        
        return result

    def get_user_permissions_summary(self, username: str) -> str:
        """ملخص صلاحيات المستخدم"""
        is_owner = self.user_manager.is_owner(username)
        is_moderator = self.user_manager.is_moderator(username)
        user_type = self.user_manager.get_user_type(username)
        emoji = self.user_manager.get_user_emoji(username)
        
        summary = f"{emoji} صلاحيات {username}:\n"
        summary += f"🏷️ النوع: {user_type}\n"
        
        if is_owner:
            summary += "✅ يمكنه استخدام جميع الأوامر\n"
            summary += "✅ إدارة المشرفين\n"
            summary += "✅ إدارة الأماكن"
        elif is_moderator:
            summary += "✅ أوامر المشرفين\n"
            summary += "✅ إدارة المستخدمين\n"
            summary += "❌ لا يمكنه إدارة المشرفين"
        else:
            summary += "✅ الأوامر العامة فقط\n"
            summary += "❌ لا يمكنه استخدام أوامر المشرفين"
        
        return summary

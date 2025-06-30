
"""
مدير أوقات الرقصات - نظام لتتبع أوقات انتهاء الرقصات مع إمكانية التحديث
"""
import asyncio
import time
import json
import os
from typing import Dict, Optional, Tuple

class EmoteTimingManager:
    def __init__(self):
        self.timing_file = "data/emote_timings.json"
        
        # قاموس أوقات الرقصات الافتراضية (بالثواني)
        self.default_durations = {
            # رقصات قصيرة (1-3 ثوانِ)
            "emoji-": 2.0,
            "emote-kiss": 2.5,
            "emote-no": 2.0,
            "emote-yes": 2.0,
            "emote-bow": 3.0,
            "emote-wave": 2.5,
            "emote-hello": 2.0,
            "emote-thumbsup": 2.0,
            "emote-clap": 3.0,
            "emote-peace": 2.5,
            "emote-point": 2.0,
            "emote-nod": 2.5,
            "emote-shake": 2.5,
            "emote-salute": 3.0,
            
            # رقصات متوسطة (3-5 ثوانِ)
            "emote-hug": 4.0,
            "emote-dab": 3.5,
            "emote-shrug": 3.0,
            "emote-flex": 4.0,
            "emote-pose": 4.5,
            "emote-curtsy": 4.0,
            "emote-confused": 3.5,
            "emote-think": 4.0,
            "emote-mad": 3.5,
            "emote-happy": 4.0,
            "emote-sad": 4.0,
            "emote-surprised": 3.5,
            "emote-embarrassed": 4.0,
            "emote-frustrated": 4.0,
            
            # رقصات طويلة (5-8 ثوانِ)
            "dance-": 6.0,
            "emote-dance": 6.5,
            "emote-robot": 5.5,
            "emote-gangnam": 7.0,
            "emote-harlemshake": 6.5,
            "emote-tapdance": 6.0,
            "emote-nightfever": 7.5,
            "emote-breakdance": 7.0,
            "emote-moonwalk": 6.0,
            "emote-disco": 6.5,
            "emote-theatrical": 7.0,
            "emote-graceful": 6.0,
            
            # رقصات خاصة طويلة جداً (8+ ثوانِ)
            "idle-": 8.0,
            "emote-snowangel": 8.5,
            "emote-zombierun": 9.0,
            "emote-superrun": 8.0,
            "emote-teleporting": 10.0,
            "emote-jetpack": 9.0,
            "emote-astronaut": 8.5,
            "emote-splitsdrop": 8.0,
            "emote-deathdrop": 8.0,
            "emote-handstand": 8.5,
            "emote-frollicking": 9.0,
            
            # رقصات تفاعلية
            "emote-proposing": 5.0,
            "emote-ropepull": 6.0,
            "emote-secrethandshake": 4.5,
            "emote-elbowbump": 3.0,
            "emote-baseball": 5.5,
            "emote-swordfight": 6.0,
            "emote-sumo": 7.0,
            
            # رقصات حالات خاصة
            "emote-sleep": 12.0,
            "emote-faint": 10.0,
            "emote-death": 10.0,
            "emote-death2": 10.0,
            
            # الرقصات الجديدة المضافة
            "idle-floating": 8.0,
            "emote-shy": 4.477567,
            "emote-tired": 4.61063,
            "dance-pinguin": 11.58291,
            "idle-guitar": 13.229398,
            "emote-stargazer": 7.320773,
            "emote-boxer": 5.555702,
            "dance-creepypuppet": 6.416121,
            "dance-anime": 8.46671,
            "emote-creepycute": 7.902453,
            "emote-headblowup": 11.667537,
            "emote-shy2": 4.989278,
            "emote-pose10": 3.989871,
            "emote-iceskating": 7.299156,
            "idle-wild": 26.0,
            "idle-nervous": 21.714221,
            "emote-timejump": 4.007305,
            "idle-toilet": 32.174447,
            "dance-jinglebell": 10.958832,
            "emote-hyped": 7.492423,
            "emote-sleigh": 11.333165,
            "emote-pose6": 5.375124,
            "dance-kawai": 10.290789,
            "dance-touch": 11.7,
            "sit-relaxed": 30.0,
            "emote-celebrationstep": 3.353703,
            "dance-employee": 8.0,
            "emote-launch": 9.4,
            "emote-cutesalute": 3.0,
            "dance-tiktok11": 11.0,
            "emote-gift": 5.0,
            "emote-pose9": 4.5,
            "emote-kissing-bound": 4.5,
            "dance-wild": 20.0,
            "idle_zombie": 28.754937,
            "idle_layingdown2": 21.546653,
            "idle-loop-tired": 21.959007,
            "idle-loop-tapdance": 6.261593,
            "idle-loop-shy": 16.47449,
            "idle-loop-sad": 6.052999,
            "idle-loop-happy": 18.798322,
            "idle-loop-annoyed": 17.058522,
            "idle-loop-aerobics": 8.507535,
            "idle-lookup": 22.339865,
            "idle-hero": 21.877099,
            "idle-dance-swinging": 13.198551,
            "idle-dance-headbobbing": 25.367458,
            "emote-attention": 4.401206,
            "emoji-ghost": 3.472759,
            "emote-lagughing": 1.125537,
            "emoji-eyeroll": 3.020264,
            "dance-sexy": 12.30883,
            "emote-puppet": 16.325823,
            "sit-open": 26.025963,
            "emote-stargaze": 1.127464,
            "emote-kawaiigogo": 10.0,
            "idle-dance-tiktok7": 12.956484,
            "emote-shrink": 8.738784,
            "emote-trampoline": 15.0,
            "emote-howl": 10.0,
            "idle-howl": 10.0,
        }
        
        # أوقات مخصصة (تحمل من الملف)
        self.custom_durations = {}
        
        # تتبع الرقصات النشطة
        self.active_emotes: Dict[str, Dict] = {}
        
        # تتبع الرقصات التلقائية
        self.auto_emotes_tracking: Dict[str, Dict] = {}
        
        # تحميل الأوقات المخصصة
        self.load_custom_timings()
        
        print("⏰ مدير أوقات الرقصات المحدث جاهز!")

    def load_custom_timings(self):
        """تحميل الأوقات المخصصة من الملف"""
        try:
            if os.path.exists(self.timing_file):
                with open(self.timing_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.custom_durations = data.get("custom_durations", {})
                print(f"📂 تم تحميل {len(self.custom_durations)} توقيت مخصص")
            else:
                os.makedirs("data", exist_ok=True)
                self.custom_durations = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل أوقات الرقصات المخصصة: {e}")
            self.custom_durations = {}

    def save_custom_timings(self):
        """حفظ الأوقات المخصصة إلى الملف"""
        try:
            # تحميل البيانات الحالية لدمج الرقصات الجديدة
            existing_data = {}
            if os.path.exists(self.timing_file):
                try:
                    with open(self.timing_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    pass
            
            # إنشاء قسم للرقصات المكتشفة حديثاً
            new_emotes = existing_data.get("new_emotes", {})
            
            # إضافة الرقصات الجديدة
            for emote_name, duration in self.custom_durations.items():
                if emote_name not in existing_data.get("custom_durations", {}):
                    new_emotes[emote_name] = duration
                    print(f"🆕 رقصة جديدة مكتشفة: {emote_name} = {duration}ث")
            
            data = {
                "custom_durations": self.custom_durations,
                "new_emotes": new_emotes,
                "last_updated": time.time()
            }
            
            with open(self.timing_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 تم حفظ {len(self.custom_durations)} توقيت مخصص ({len(new_emotes)} جديدة)")
        except Exception as e:
            print(f"❌ خطأ في حفظ أوقات الرقصات: {e}")

    def get_emote_duration(self, emote_name: str) -> float:
        """الحصول على مدة الرقصة"""
        # أولاً: البحث في الأوقات المخصصة
        if emote_name in self.custom_durations:
            return self.custom_durations[emote_name]
        
        # ثانياً: البحث في الأوقات الافتراضية
        emote_lower = emote_name.lower()
        for prefix, duration in self.default_durations.items():
            if emote_lower.startswith(prefix):
                return duration
        
        # الافتراضي للرقصات غير المعروفة
        return 4.5

    def update_emote_duration(self, emote_name: str, duration: float) -> bool:
        """تحديث مدة رقصة معينة"""
        try:
            if duration < 0.5 or duration > 60:
                return False
            
            self.custom_durations[emote_name] = duration
            self.save_custom_timings()
            return True
        except Exception as e:
            print(f"خطأ في تحديث مدة الرقصة {emote_name}: {e}")
            return False

    def update_multiple_durations(self, emote_timings: Dict[str, float]) -> int:
        """تحديث أوقات متعددة"""
        updated_count = 0
        try:
            for emote_name, duration in emote_timings.items():
                if 0.5 <= duration <= 60:
                    self.custom_durations[emote_name] = duration
                    updated_count += 1
            
            self.save_custom_timings()
            return updated_count
        except Exception as e:
            print(f"خطأ في تحديث أوقات متعددة: {e}")
            return 0

    def reset_emote_duration(self, emote_name: str) -> bool:
        """إعادة تعيين مدة رقصة للقيمة الافتراضية"""
        try:
            if emote_name in self.custom_durations:
                del self.custom_durations[emote_name]
                self.save_custom_timings()
                return True
            return False
        except Exception as e:
            print(f"خطأ في إعادة تعيين مدة الرقصة {emote_name}: {e}")
            return False

    def reset_all_durations(self) -> bool:
        """إعادة تعيين جميع الأوقات للقيم الافتراضية"""
        try:
            self.custom_durations = {}
            self.save_custom_timings()
            return True
        except Exception as e:
            print(f"خطأ في إعادة تعيين جميع الأوقات: {e}")
            return False

    def get_all_emote_timings(self, emotes_list: list) -> list:
        """الحصول على قائمة بجميع أوقات الرقصات"""
        timings = []
        for i, emote_name in enumerate(emotes_list):
            timings.append({
                "number": i + 1,
                "name": emote_name,
                "duration": self.get_emote_duration(emote_name),
                "is_custom": emote_name in self.custom_durations,
                "category": self.get_emote_type_category(emote_name)
            })
        return timings

    def start_emote_tracking(self, user_id: str, username: str, emote_name: str, is_auto: bool = False) -> Dict:
        """بدء تتبع رقصة جديدة"""
        current_time = time.time()
        duration = self.get_emote_duration(emote_name)
        end_time = current_time + duration
        
        emote_info = {
            "emote": emote_name,
            "username": username,
            "start_time": current_time,
            "duration": duration,
            "end_time": end_time,
            "is_auto": is_auto,
            "status": "active"
        }
        
        self.active_emotes[user_id] = emote_info
        
        if is_auto:
            if user_id not in self.auto_emotes_tracking:
                self.auto_emotes_tracking[user_id] = {
                    "emote": emote_name,
                    "username": username,
                    "loop_count": 0,
                    "total_time": 0,
                    "start_session": current_time
                }
            
            self.auto_emotes_tracking[user_id]["loop_count"] += 1
            self.auto_emotes_tracking[user_id]["total_time"] += duration
        
        return emote_info

    def stop_emote_tracking(self, user_id: str) -> Optional[Dict]:
        """إيقاف تتبع الرقصة"""
        if user_id in self.active_emotes:
            emote_info = self.active_emotes[user_id]
            emote_info["status"] = "stopped"
            emote_info["actual_end_time"] = time.time()
            
            stopped_info = emote_info.copy()
            del self.active_emotes[user_id]
            
            return stopped_info
        return None

    def stop_auto_emote_tracking(self, user_id: str) -> Optional[Dict]:
        """إيقاف تتبع الرقصة التلقائية"""
        self.stop_emote_tracking(user_id)
        
        if user_id in self.auto_emotes_tracking:
            tracking_info = self.auto_emotes_tracking[user_id]
            tracking_info["end_session"] = time.time()
            tracking_info["session_duration"] = tracking_info["end_session"] - tracking_info["start_session"]
            
            stopped_tracking = tracking_info.copy()
            del self.auto_emotes_tracking[user_id]
            
            return stopped_tracking
        return None

    def get_remaining_time(self, user_id: str) -> Optional[float]:
        """الحصول على الوقت المتبقي للرقصة"""
        if user_id in self.active_emotes:
            current_time = time.time()
            end_time = self.active_emotes[user_id]["end_time"]
            remaining = end_time - current_time
            return max(0, remaining)
        return None

    def get_active_emotes_info(self) -> Dict:
        """الحصول على معلومات جميع الرقصات النشطة"""
        current_time = time.time()
        active_info = {}
        
        for user_id, emote_info in self.active_emotes.items():
            remaining = emote_info["end_time"] - current_time
            active_info[user_id] = {
                "username": emote_info["username"],
                "emote": emote_info["emote"],
                "duration": emote_info["duration"],
                "remaining": max(0, remaining),
                "progress": min(100, ((emote_info["duration"] - remaining) / emote_info["duration"]) * 100),
                "is_auto": emote_info["is_auto"]
            }
        
        return active_info

    def get_auto_emotes_stats(self) -> Dict:
        """الحصول على إحصائيات الرقصات التلقائية"""
        current_time = time.time()
        stats = {}
        
        for user_id, tracking_info in self.auto_emotes_tracking.items():
            session_duration = current_time - tracking_info["start_session"]
            stats[user_id] = {
                "username": tracking_info["username"],
                "emote": tracking_info["emote"],
                "loop_count": tracking_info["loop_count"],
                "total_emote_time": tracking_info["total_time"],
                "session_duration": session_duration,
                "efficiency": (tracking_info["total_time"] / session_duration) * 100 if session_duration > 0 else 0
            }
        
        return stats

    def cleanup_expired_emotes(self) -> list:
        """تنظيف الرقصات المنتهية الصلاحية"""
        current_time = time.time()
        expired_users = []
        
        for user_id, emote_info in list(self.active_emotes.items()):
            if current_time >= emote_info["end_time"]:
                expired_users.append({
                    "user_id": user_id,
                    "username": emote_info["username"],
                    "emote": emote_info["emote"]
                })
                del self.active_emotes[user_id]
        
        return expired_users

    def get_emote_type_category(self, emote_name: str) -> str:
        """تصنيف الرقصة حسب النوع"""
        emote_lower = emote_name.lower()
        
        if emote_lower.startswith("emoji-"):
            return "تعبير"
        elif emote_lower.startswith("dance-"):
            return "رقص"
        elif emote_lower.startswith("idle-"):
            return "استراحة"
        elif emote_lower.startswith("emote-dance"):
            return "رقص"
        elif emote_lower.startswith("emote-pose"):
            return "وضعية"
        elif any(x in emote_lower for x in ["fight", "kick", "punch", "sword"]):
            return "قتال"
        elif any(x in emote_lower for x in ["sleep", "tired", "relax", "laying"]):
            return "راحة"
        else:
            return "عام"

    def get_timing_report(self, user_id: str = None) -> str:
        """تقرير مفصل عن أوقات الرقصات"""
        if user_id:
            if user_id in self.active_emotes:
                info = self.active_emotes[user_id]
                remaining = self.get_remaining_time(user_id)
                progress = ((info["duration"] - remaining) / info["duration"]) * 100
                
                report = f"⏰ تقرير الرقصة لـ {info['username']}:\n"
                report += f"🎭 الرقصة: {info['emote']}\n"
                report += f"⏳ المدة الكاملة: {info['duration']:.1f} ثانية\n"
                report += f"⏰ المتبقي: {remaining:.1f} ثانية\n"
                report += f"📊 التقدم: {progress:.1f}%\n"
                report += f"🏷️ النوع: {self.get_emote_type_category(info['emote'])}\n"
                report += f"🔄 تلقائية: {'نعم' if info['is_auto'] else 'لا'}"
                
                return report
            else:
                return f"❌ لا توجد رقصة نشطة للمستخدم"
        else:
            active_info = self.get_active_emotes_info()
            auto_stats = self.get_auto_emotes_stats()
            
            if not active_info and not auto_stats:
                return "📭 لا توجد رقصات نشطة حالياً"
            
            report = "⏰ تقرير الرقصات النشطة:\n\n"
            
            if active_info:
                report += "🎭 الرقصات الحالية:\n"
                for user_id, info in active_info.items():
                    report += f"• {info['username']}: {info['emote']} "
                    report += f"({info['remaining']:.1f}ث متبقية، {info['progress']:.0f}%)\n"
                report += "\n"
            
            if auto_stats:
                report += "🔄 الرقصات التلقائية:\n"
                for user_id, stats in auto_stats.items():
                    report += f"• {stats['username']}: {stats['emote']} "
                    report += f"(تكرار: {stats['loop_count']}, كفاءة: {stats['efficiency']:.1f}%)\n"
            
            return report

    async def start_cleanup_task(self):
        """مهمة تنظيف دورية للرقصات المنتهية"""
        while True:
            try:
                expired = self.cleanup_expired_emotes()
                if expired:
                    print(f"🧹 تم تنظيف {len(expired)} رقصة منتهية")
                
                await asyncio.sleep(5)
            except Exception as e:
                print(f"خطأ في تنظيف الرقصات: {e}")
                await asyncio.sleep(10)

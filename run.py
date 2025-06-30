from flask import Flask, render_template, jsonify, request
from threading import Thread
from highrise.__main__ import *
from highrise.models import Item
import time
import json
import os
import zipfile
from datetime import datetime
from modules.update_manager import UpdateManager


class WebServer():

  def __init__(self):
    self.app = Flask(__name__)
    self.current_room_users = []  # قائمة المستخدمين الحاليين
    self.update_manager = UpdateManager()  # مدير التحديثات
    global bot_instance

    @self.app.route('/')
    def index() -> str:
      return render_template('index.html')

    @self.app.route('/outfits')
    def outfits():
      return render_template('outfits.html')

    @self.app.route('/updates')
    def updates():
      return render_template('updates.html')

    @self.app.route('/api/emotes')
    def get_emotes():
      """API لجلب قائمة الرقصات"""
      try:
        # محاولة تحميل من ملف البيانات أولاً
        if os.path.exists('data/emotes_data.json'):
          with open('data/emotes_data.json', 'r', encoding='utf-8') as f:
            emotes_data = json.load(f)

          # التأكد من وجود قائمة الرقصات
          if 'emotes_list' in emotes_data:
            return jsonify({
              "success": True,
              "emotes": emotes_data['emotes_list'],
              "emotes_list": emotes_data['emotes_list'],
              "total_emotes": len(emotes_data['emotes_list'])
            })

        # إذا لم يكن الملف موجود، استخدم قائمة افتراضية
        if hasattr(bot_instance, 'emotes_manager') and bot_instance.emotes_manager:
          emotes_list = bot_instance.emotes_manager.emotes_list
          return jsonify({
            "success": True,
            "emotes": emotes_list,
            "emotes_list": emotes_list,
            "total_emotes": len(emotes_list)
          })

        # قائمة احتياطية
        default_emotes = ["emote-superpose", "emote-frog", "dance-tiktok10", "dance-weird", "idle-fighter"]
        return jsonify({
          "success": True,
          "emotes": default_emotes,
          "emotes_list": default_emotes,
          "total_emotes": len(default_emotes)
        })

      except Exception as e:
        print(f"❌ خطأ في API الرقصات: {e}")
        return jsonify({
          "success": False,
          "error": f"فشل في تحميل بيانات الرقصات: {str(e)}",
          "emotes": [],
          "emotes_list": []
        })

    @self.app.route('/api/users')
    def get_users():
      """API للحصول على المستخدمين"""
      try:
        # تحويل البيانات إلى تنسيق JSON-serializable
        users_list = []
        for user_id, user_data in bot_instance.user_manager.users.items():
            users_list.append({
                'id': user_id,
                'username': user_data.get('username', 'غير معروف'),
                'user_type': user_data.get('user_type', 'مستخدم عادي'),
                'visit_count': user_data.get('visit_count', 0),
                'first_seen': user_data.get('first_seen', ''),
                'last_seen': user_data.get('last_seen', ''),
                'is_active': user_data.get('is_active', False)
            })

        return jsonify({
            'success': True,
            'users': users_list,
            'total_count': len(users_list)
        })
      except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    @self.app.route('/api/status')
    def api_status():
      return jsonify({
        'message': 'البوت متصل ونشط',
        'timestamp': time.time(),
        'success': True
      })

    @self.app.route('/api/change-outfit', methods=['POST'])
    def change_outfit():
      try:
        data = request.get_json()
        outfit = data.get('outfit', {})

        if not outfit:
          return jsonify({'success': False, 'error': 'لم يتم تحديد ملابس'})

        # بناء قائمة بقطع الملابس المختارة
        outfit_items = []

        for category, item_data in outfit.items():
          # التعامل مع البيانات سواء كانت string أو dictionary
          if isinstance(item_data, dict):
            item_id = item_data.get('id', '')
          else:
            item_id = str(item_data) if item_data else ''

          if item_id and item_id != 'none':
            outfit_items.append(Item(type='clothing', amount=1, id=item_id, account_bound=False, active_palette=-1))

        # كتابة أمر تغيير الملابس للبوت
        outfit_command = f"تغيير {' '.join([item.id for item in outfit_items])}"
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(outfit_command)

        return jsonify({
          'success': True,
          'message': f'تم إرسال أمر تغيير الزي ({len(outfit_items)} قطعة)'
        })

      except Exception as e:
        print(f"خطأ في تغيير الزي: {e}")
        return jsonify({'success': False, 'error': str(e)})

    @self.app.route('/api/outfits')
    def get_outfits():
        """الحصول على بيانات الملابس"""
        try:
            # قائمة الملابس المتاحة
            outfits_data = {
                "hair_front": [
                    {"id": "hair_front-n_malenew33", "name": "Short Short Fro"},
                    {"id": "hair_front-n_malenew32", "name": "Box Braids"},
                    {"id": "hair_front-n_malenew31", "name": "Long Undercut Dreads"},
                    {"id": "hair_front-n_malenew30", "name": "Undercut Dreads"},
                    {"id": "hair_front-n_malenew29", "name": "Side Swept Fro"},
                    {"id": "hair_front-n_malenew27", "name": "Long Buzzed Fro"},
                    {"id": "hair_front-n_malenew26", "name": "Short Buzzed Fro"},
                    {"id": "hair_front-n_malenew25", "name": "Curly Undercut"},
                    {"id": "hair_front-n_malenew24", "name": "Tight curls"},
                    {"id": "hair_front-n_malenew23", "name": "Loose Curls"},
                    {"id": "hair_front-n_malenew22", "name": "Shaggy Curls"},
                    {"id": "hair_front-n_malenew21", "name": "Short Curls"},
                    {"id": "hair_front-n_malenew20", "name": "Medium Wavy Cut"},
                    {"id": "hair_front-n_malenew19", "name": "Short Wavy Cut"},
                    {"id": "hair_front-n_malenew18", "name": "Wavy Undercut"},
                    {"id": "hair_front-n_malenew17", "name": "Wavy Side Part"},
                    {"id": "hair_front-n_malenew16", "name": "Shaggy Side Part"},
                    {"id": "hair_front-n_malenew15", "name": "Combed Back Waves"},
                    {"id": "hair_front-n_malenew14", "name": "Blown Back Waves"},
                    {"id": "hair_front-n_malenew13", "name": "Short Straight"},
                    {"id": "hair_front-n_malenew12", "name": "Side Combed Straight"},
                    {"id": "hair_front-n_malenew11", "name": "Straight Slicked Back"},
                    {"id": "hair_front-n_malenew10", "name": "Buzz Cut"},
                    {"id": "hair_front-n_malenew09", "name": "Shaggy Crew Cut"},
                    {"id": "hair_front-n_malenew08", "name": "Faux Hawk"},
                    {"id": "hair_front-n_malenew07", "name": "Shaggy Straight"},
                    {"id": "hair_front-n_malenew06", "name": "Straight Side Part"},
                    {"id": "hair_front-n_malenew05", "name": "Combed Back Undercut"},
                    {"id": "hair_front-n_malenew04", "name": "Upward Swoosh"},
                    {"id": "hair_front-n_malenew03", "name": "Side Swept Undercut"},
                    {"id": "hair_front-n_malenew02", "name": "Side Swept"},
                    {"id": "hair_front-n_malenew01", "name": "Crew Cut"}
                ],
                "hair_back": [
                    {"id": "hair_back-n_malenew33", "name": "Short Short Fro"},
                    {"id": "hair_back-n_malenew32", "name": "Box Braids"},
                    {"id": "hair_back-n_malenew31", "name": "Long Undercut Dreads"},
                    {"id": "hair_back-n_malenew30", "name": "Undercut Dreads"},
                    {"id": "hair_back-n_malenew29", "name": "Side Swept Fro"},
                    {"id": "hair_back-n_malenew27", "name": "Long Buzzed Fro"},
                    {"id": "hair_back-n_malenew26", "name": "Short Buzzed Fro"},
                    {"id": "hair_back-n_malenew25", "name": "Curly Undercut"},
                    {"id": "hair_back-n_malenew24", "name": "Tight Curls"},
                    {"id": "hair_back-n_malenew23", "name": "Loose Curls"},
                    {"id": "hair_back-n_malenew22", "name": "Shaggy Curls"},
                    {"id": "hair_back-n_malenew21", "name": "Short Curls"},
                    {"id": "hair_back-n_malenew20", "name": "Medium Wavy Cut"},
                    {"id": "hair_back-n_malenew19", "name": "Short Wavy Cut"},
                    {"id": "hair_back-n_malenew18", "name": "Wavy Undercut"},
                    {"id": "hair_back-n_malenew17", "name": "Wavy Side Part"},
                    {"id": "hair_back-n_malenew16", "name": "Shaggy Side Part"},
                    {"id": "hair_back-n_malenew15", "name": "Combed Back Waves"},
                    {"id": "hair_back-n_malenew14", "name": "Blown Back Waves"},
                    {"id": "hair_back-n_malenew13", "name": "Short Straight"},
                    {"id": "hair_back-n_malenew12", "name": "Side Combed Straight"},
                    {"id": "hair_back-n_malenew11", "name": "Straight Slicked Back"},
                    {"id": "hair_back-n_malenew10", "name": "Buzz Cut"},
                    {"id": "hair_back-n_malenew09", "name": "Shaggy Crew Cut"},
                    {"id": "hair_back-n_malenew08", "name": "Faux Hawk"},
                    {"id": "hair_back-n_malenew07", "name": "Shaggy Straight"},
                    {"id": "hair_back-n_malenew06", "name": "Straight Side Part"},
                    {"id": "hair_back-n_malenew05", "name": "Combed Back Undercut"},
                    {"id": "hair_back-n_malenew04", "name": "Upward Swoosh"},
                    {"id": "hair_back-n_malenew03", "name": "Side Swept Undercut"},
                    {"id": "hair_back-n_malenew02", "name": "Side Swept"},
                    {"id": "hair_back-n_malenew01", "name": "Crew Cut"}
                ],
                "pants": [
                    {"id": "shorts-f_pantyhoseshortsnavy", "name": "Navy Shorts w/ Pantyhose"},
                    {"id": "pants-n_starteritems2019mensshortswhite", "name": "Basic Shorts - White"},
                    {"id": "pants-n_starteritems2019mensshortsblue", "name": "Basic Shorts - Blue"},
                    {"id": "pants-n_starteritems2019mensshortsblack", "name": "Basic Shorts - Black"},
                    {"id": "pants-n_starteritems2019cuffedshortswhite", "name": "Cuffed Shorts - White"},
                    {"id": "pants-n_starteritems2019cuffedshortsblue", "name": "Cuffed Shorts - Blue"},
                    {"id": "pants-n_starteritems2019cuffedshortsblack", "name": "Cuffed Shorts - Black"},
                    {"id": "pants-n_starteritems2019cuffedjeanswhite", "name": "Cuffed Jeans - White"},
                    {"id": "pants-n_starteritems2019cuffedjeansblue", "name": "Cuffed Jeans - Blue"},
                    {"id": "pants-n_starteritems2019cuffedjeansblack", "name": "Cuffed Jeans - Black"},
                    {"id": "pants-n_room32019rippedpantswhite", "name": "Ripped White Jeans"},
                    {"id": "pants-n_room32019rippedpantsblue", "name": "Ripped Blue Jeans"},
                    {"id": "pants-n_room32019longtrackshortscamo", "name": "Camo Track Shorts"},
                    {"id": "pants-n_room32019longshortswithsocksgrey", "name": "Grey Long Shorts"},
                    {"id": "pants-n_room32019longshortswithsocksblack", "name": "Black Long Shorts"},
                    {"id": "pants-n_room32019highwasittrackshortsblack", "name": "Short Black Track Shorts"},
                    {"id": "pants-n_room32019baggytrackpantsred", "name": "Red Baggy Trackpants"},
                    {"id": "pants-n_room32019baggytrackpantsgreycamo", "name": "Grey Camo Baggy Trackpants"},
                    {"id": "pants-n_room22019undiespink", "name": "Pink Undies"},
                    {"id": "pants-n_room22019undiesblack", "name": "Black Undies"},
                    {"id": "pants-n_room22019techpantscamo", "name": "Camo Tech Pants"},
                    {"id": "pants-n_room22019shortcutoffsdenim", "name": "Short Denim Cut-Offs"},
                    {"id": "pants-n_room22019longcutoffsdenim", "name": "Denim Cut-Offs"},
                    {"id": "pants-n_room12019rippedpantsblue", "name": "Ripped Blue Denim"},
                    {"id": "pants-n_room12019rippedpantsblack", "name": "Ripped Black Denim"},
                    {"id": "pants-n_room12019formalslackskhaki", "name": "Khaki Formal Slacks"},
                    {"id": "pants-n_room12019formalslacksblack", "name": "Plain Black Formal Slacks"},
                    {"id": "pants-n_room12019blackacidwashjeans", "name": "Plain Black Acid Wash Jeans"},
                    {"id": "pants-n_2016fallgreyacidwashjeans", "name": "Grey Acid Wash"}
                ],
                "skirts": [
                    {"id": "skirt-n_starteritems2018whiteskirt", "name": "Basic Skirt - White"},
                    {"id": "skirt-n_starteritems2018blueskirt", "name": "Basic Skirt - Blue"},
                    {"id": "skirt-n_starteritems2018blackskirt", "name": "Basic Skirt - Black"},
                    {"id": "skirt-n_room22019skirtwithsocksplaid", "name": "Plaid Skirt With Socks"},
                    {"id": "skirt-n_room22019skirtwithsocksblack", "name": "Black Skirt With Socks"},
                    {"id": "skirt-n_room12019pleatedskirtpink", "name": "Pleated Pink Skirt"},
                    {"id": "skirt-n_room12019pleatedskirtgrey", "name": "Pleated Skirt Grey"},
                    {"id": "skirt-n_room12019pleatedskirtblack", "name": "Pleated Black Skirt"},
                    {"id": "skirt-f_gianttutu", "name": "Tutu"}
                ],
                "eyes": [
                    {"id": "eye-n_basic2018zanyeyes", "name": "Zany Eyes"},
                    {"id": "eye-n_basic2018woaheyes", "name": "Woah Eyes"},
                    {"id": "eye-n_basic2018wingedliner", "name": "Winged Eyeliner"},
                    {"id": "eye-n_basic2018teardrop", "name": "Tear Drop Eyes"},
                    {"id": "eye-n_basic2018starryeye", "name": "Starry Eye"},
                    {"id": "eye-n_basic2018squintynude", "name": "Squinty Nude Eye"},
                    {"id": "eye-n_basic2018snakeeyes", "name": "Snake Eyes"},
                    {"id": "eye-n_basic2018smokeyeye2", "name": "Dark Shadow"},
                    {"id": "eye-n_basic2018slantednude", "name": "Slanted Nude Eye"},
                    {"id": "eye-n_basic2018redeyes", "name": "Red Eyes"},
                    {"id": "eye-n_basic2018pinkshadow2", "name": "Light Shadow"},
                    {"id": "eye-n_basic2018nudesquare", "name": "Square Nude Eye"},
                    {"id": "eye-n_basic2018nudediamond", "name": "Diamond Nude Eye"},
                    {"id": "eye-n_basic2018malesquareupturned", "name": "Upturned Square (masc)"},
                    {"id": "eye-n_basic2018malesquaresquint", "name": "Squinty Square (masc)"},
                    {"id": "eye-n_basic2018malesquaresleepy", "name": "Sleepy Square (masc)"},
                    {"id": "eye-n_basic2018malesquaredroopy", "name": "Droopy Square (masc)"},
                    {"id": "eye-n_basic2018malesquare", "name": "Square (masculine)"},
                    {"id": "eye-n_basic2018maleroundupturned", "name": "Upturned Round (masc)"},
                    {"id": "eye-n_basic2018maleroundsquint", "name": "Squinty Round (masc)"},
                    {"id": "eye-n_basic2018maleroundsleepy", "name": "Sleepy Round (masc)"},
                    {"id": "eye-n_basic2018malerounddroopy", "name": "Droopy Round (masc)"},
                    {"id": "eye-n_basic2018maleround", "name": "Round (masculine)"},
                    {"id": "eye-n_basic2018malediamondupturned", "name": "Upturned Diamond (masc)"},
                    {"id": "eye-n_basic2018malediamondsquint", "name": "Squinty Diamond (masc)"},
                    {"id": "eye-n_basic2018malediamondsleepy", "name": "Sleepy Diamond (masc)"},
                    {"id": "eye-n_basic2018malediamonddroopy", "name": "Droopy Diamond (masc)"},
                    {"id": "eye-n_basic2018malediamond", "name": "Diamond (masculine)"},
                    {"id": "eye-n_basic2018malealmondupturned", "name": "Upturned Almond (masc)"},
                    {"id": "eye-n_basic2018malealmondsquint", "name": "Squinty Almond (masc)"},
                    {"id": "eye-n_basic2018malealmond", "name": "Almond (masculine)"},
                    {"id": "eye-n_basic2018liftedeyes", "name": "Lifted Eyes"},
                    {"id": "eye-n_basic2018holloweyes", "name": "Empty Eyes"},
                    {"id": "eye-n_basic2018heavymascera", "name": "Heavy Mascara"},
                    {"id": "eye-n_basic2018guyliner", "name": "Guy Liner"},
                    {"id": "eye-n_basic2018goldshadow2", "name": "Earthy Shadow"},
                    {"id": "eye-n_basic2018femalesquareupturned", "name": "Upturned Square (fem)"},
                    {"id": "eye-n_basic2018femalesquaresquint", "name": "Squinty Square (fem)"},
                    {"id": "eye-n_basic2018femalesquaresleepy", "name": "Sleepy Square (fem)"},
                    {"id": "eye-n_basic2018femalesquaredroopy", "name": "Droopy Square (fem)"},
                    {"id": "eye-n_basic2018femalesquare", "name": "Square (Feminine)"},
                    {"id": "eye-n_basic2018femalesovalsquint", "name": "Squinty Oval (fem)"},
                    {"id": "eye-n_basic2018femaleroundupturned", "name": "Upturned Round (fem)"},
                    {"id": "eye-n_basic2018femaleroundsleepy", "name": "Sleepy Round (fem)"},
                    {"id": "eye-n_basic2018femalerounddroopy", "name": "Droopy Round (fem)"},
                    {"id": "eye-n_basic2018femaleround", "name": "Round (feminine)"},
                    {"id": "eye-n_basic2018femaleovalslant", "name": "Slanted Oval (fem)"},
                    {"id": "eye-n_basic2018femaleovaldroopy", "name": "Droopy Oval (fem)"},
                    {"id": "eye-n_basic2018femalediamondupturned", "name": "Upturned Diamond (fem)"},
                    {"id": "eye-n_basic2018femalediamondsquint", "name": "Squinty Diamond (fem)"},
                    {"id": "eye-n_basic2018femalediamondsleepy", "name": "Sleepy Diamond (fem)"},
                    {"id": "eye-n_basic2018femalediamond", "name": "Diamond (Feminine)"},
                    {"id": "eye-n_basic2018femalealmoundsquint", "name": "Squinty Almond (fem)"},
                    {"id": "eye-n_basic2018femalealmond", "name": "Almond (Feminine)"},
                    {"id": "eye-n_basic2018falselashes", "name": "False Eyelashes"},
                    {"id": "eye-n_basic2018downturnedoval", "name": "Downturned Oval"},
                    {"id": "eye-n_basic2018doublewing", "name": "Double Wing Eyeliner"},
                    {"id": "eye-n_basic2018dolleyes", "name": "Doll Eyes"},
                    {"id": "eye-n_basic2018doeeyes", "name": "Doe Eyes"},
                    {"id": "eye-n_basic2018definedlashes", "name": "Defined Lashes"},
                    {"id": "eye-n_basic2018crescent", "name": "Squinty Crescent"},
                    {"id": "eye-n_basic2018butterflyeyes", "name": "Butterfly Eyes"},
                    {"id": "eye-n_basic2018blockeyes", "name": "Blocky Eyes"},
                    {"id": "eye-n_basic2018animeeyes", "name": "Basic Anime Eyes"},
                    {"id": "eye-n_basic2018angryeyes", "name": "Angry Eyes"}
                ]
            }

            return jsonify({
                'success': True,
                'outfits': outfits_data,
                'categories': len(outfits_data)
            })
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات الملابس: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @self.app.route('/api/current-outfit')
    def current_outfit():
      try:
        # في الوقت الحالي، نرجع رسالة بسيطة
        # يمكن تطوير هذا لاحقاً لحفظ واسترجاع الزي الحالي
        return jsonify({
          'success': True,
          'outfit': {
            'hair': 'شعر افتراضي',
            'shirt': 'قميص افتراضي',
            'pants': 'بنطلون افتراضي'
          }
        })
      except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    @self.app.route('/api/dance', methods=['POST'])
    def dance_user():
      """API لجعل مستخدم يرقص"""
      try:
        data = request.get_json()
        username = data.get('username', '').strip()
        emote_number = data.get('emote_number', 1)

        if not username:
          return jsonify({"error": "اسم المستخدم مطلوب"})

        # هنا يمكن إضافة منطق لجعل المستخدم يرقص
        # سيتم تنفيذه عبر البوت
        return jsonify({
          "success": True,
          "message": f"تم إرسال أمر الرقص للمستخدم {username}"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/dance/stop', methods=['POST'])
    def stop_dance():
      """API لإيقاف الرقص"""
      try:
        data = request.get_json()
        username = data.get('username', '').strip()

        return jsonify({
          "success": True,
          "message": f"تم إيقاف الرقص للمستخدم {username}"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/bot-auto-emote/start', methods=['POST'])
    def start_bot_auto_emote():
      """API لبدء الرقص التلقائي للبوت"""
      try:
        # تشغيل رقص البوت عبر كتابة الأمر في ملف
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write('bot_dance')

        return jsonify({
          "success": True,
          "message": "تم بدء الرقص التلقائي للبوت"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/user-repeated-emote/start', methods=['POST'])
    def start_user_repeated_emote():
      """API لبدء الرقص المتكرر لمستخدم محدد"""
      try:
        data = request.get_json()
        username = data.get('username', '').strip()
        emote_number = data.get('emote_number', 1)

        if not username:
          return jsonify({"error": "اسم المستخدم مطلوب"})

        if not (1 <= emote_number <= 183):
          return jsonify({"error": "رقم الرقصة يجب أن يكون بين 1 و 183"})

        # إرسال الأمر عبر ملف مؤقت
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(f'رقص {emote_number} @{username}')

        return jsonify({
          "success": True,
          "message": f"تم إرسال أمر الرقص المتكرر رقم {emote_number} للمستخدم {username}"
        })

      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/user-repeated-emote/stop', methods=['POST'])
    def stop_user_repeated_emote():
      """API لإيقاف الرقص المتكرر لمستخدم محدد"""
      try:
        data = request.get_json()
        username = data.get('username', '').strip()

        if not username:
          return jsonify({"error": "اسم المستخدم مطلوب"})

        # إرسال الأمر عبر ملف مؤقت
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(f'ايقاف @{username}')

        return jsonify({
          "success": True,
          "message": f"تم إرسال أمر إيقاف الرقص للمستخدم {username}"
        })

      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/group-emote/start', methods=['POST'])
    def start_group_emote():
      """API لبدء رقصة جماعية لجميع المستخدمين"""
      try:
        data = request.get_json()
        emote_number = data.get('emote_number', 1)

        if not (1 <= emote_number <= 183):
          return jsonify({"error": "رقم الرقصة يجب أن يكون بين 1 و 183"})

        # إرسال الأمر عبر ملف مؤقت
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(f'رقص_الكل {emote_number}')

        return jsonify({
          "success": True,
          "message": f"تم إرسال أمر الرقصة الجماعية رقم {emote_number}"
        })

      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/bot-auto-emote/stop', methods=['POST'])
    def stop_bot_auto_emote():
      """API لإيقاف الرقص التلقائي للبوت"""
      try:
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write('bot_dance_stop')

        return jsonify({
          "success": True,
          "message": "تم إيقاف الرقص التلقائي للبوت"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/random-emote-all', methods=['POST'])
    def random_emote_all():
      """API لرقصة عشوائية لجميع المستخدمين"""
      try:
        return jsonify({
          "success": True,
          "message": "تم تنفيذ رقصة عشوائية لجميع المستخدمين"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/stop-all-emotes', methods=['POST'])
    def stop_all_emotes():
      """API لإيقاف جميع الرقصات"""
      try:
        return jsonify({
          "success": True,
          "message": "تم إيقاف جميع الرقصات"
        })
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/room-users', methods=['GET'])
    def get_room_users():
      """API للحصول على المستخدمين الحاليين في الغرفة"""
      try:
        # كتابة ملف طلب الحصول على المستخدمين
        with open('temp_get_users.txt', 'w') as f:
          f.write('get_users')

        # انتظار الاستجابة
        timeout = 10
        start_time = time.time()

        while not os.path.exists('temp_users_response.json'):
          if time.time() - start_time > timeout:
            return jsonify({'error': 'timeout'}), 408
          time.sleep(0.1)

        # قراءة الاستجابة
        with open('temp_users_response.json', 'r', encoding='utf-8') as f:
          users_data = json.load(f)

        # تنظيف الملف
        os.remove('temp_users_response.json')

        print(f"📊 تم الحصول على {len(users_data)} مستخدم من الغرفة")
        return jsonify({
            'success': True,
            'users': users_data,
            'count': len(users_data)
        })

      except Exception as e:
        print(f"خطأ في API المستخدمين: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'users': []
        }), 500

    @self.app.route('/api/location-stats')
    def get_location_stats():
      """الحصول على إحصائيات نظام تتبع المواقع"""
      try:
        if not os.path.exists('data/user_locations.json'):
          return jsonify({'stats': 'لا توجد مواقع محفوظة'})

        with open('data/user_locations.json', 'r', encoding='utf-8') as f:
          locations = json.load(f)

        total_users = len(locations)
        if total_users == 0:
          return jsonify({'stats': 'لا توجد مواقع محفوظة'})

        # حساب الإحصائيات
        avg_x = sum(data.get("x", 0) for data in locations.values()) / total_users
        avg_z = sum(data.get("z", 0) for data in locations.values()) / total_users

        stats = {
          'total_users': total_users,
          'avg_position': {'x': round(avg_x, 1), 'z': round(avg_z, 1)},
          'last_update': datetime.now().strftime('%H:%M:%S')
        }

        return jsonify({'stats': stats})

      except Exception as e:
        return jsonify({'error': str(e)}), 500

    @self.app.route('/api/user-location/<username>')
    def get_user_location(username):
      """الحصول على موقع مستخدم محدد"""
      try:
        if not os.path.exists('data/user_locations.json'):
          return jsonify({'error': 'لا توجد مواقع محفوظة'})

        with open('data/user_locations.json', 'r', encoding='utf-8') as f:
          locations = json.load(f)

        for user_id, data in locations.items():
          if data["username"].lower() == username.lower():
            return jsonify({'location': data})

        return jsonify({'error': f'لم يتم العثور على موقع المستخدم {username}'})

      except Exception as e:
        return jsonify({'error': str(e)}), 500

    @self.app.route('/api/send-reactions', methods=['POST'])
    def send_reactions():
      """API لإرسال ريأكشنز لجميع المستخدمين"""
      try:
        data = request.get_json()
        reaction_type = data.get('reaction_type', '')

        if reaction_type in ['heart', 'wave', 'thumbs', 'clap']:
          # كتابة الأمر في ملف مؤقت للتنفيذ
          with open('temp_command.txt', 'w', encoding='utf-8') as f:
            f.write(f'send_reaction_all:{reaction_type}')

          return jsonify({
            "success": True,
            "message": f"تم إرسال {reaction_type} لجميع المستخدمين"
          })
        else:
          return jsonify({"error": "نوع ريأكشن غير صحيح"})
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/execute-command', methods=['POST'])
    def execute_command():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'لا توجد بيانات'})

            command = data.get('command', '').strip()

            if not command:
                return jsonify({'success': False, 'error': 'لا يوجد أمر للتنفيذ'})

            print(f"📝 تنفيذ أمر مؤقت: {command}")

            # كتابة الأمر في ملف مؤقت
            with open('temp_command.txt', 'w', encoding='utf-8') as f:
                f.write(command)

            # انتظار قصير للتأكد من كتابة الملف
            import time
            time.sleep(0.1)

            return jsonify({'success': True, 'message': f'تم إرسال الأمر: {command}'}), 200

        except Exception as e:
            print(f"❌ خطأ في تنفيذ الأمر: {e}")
            return jsonify({'success': False, 'error': f'خطأ في الخادم: {str(e)}'}), 500

    @self.app.route('/api/emote-timing', methods=['GET'])
    def get_emote_timing():
      """API للحصول على معلومات أوقات الرقصات"""
      try:
        if hasattr(bot_instance, 'emote_timing') and bot_instance.emote_timing:
          active_emotes = bot_instance.emote_timing.get_active_emotes_info()
          auto_stats = bot_instance.emote_timing.get_auto_emotes_stats()

          return jsonify({
            "active_emotes": active_emotes,
            "auto_emotes_stats": auto_stats,
            "total_active": len(active_emotes),
            "total_auto": len(auto_stats)
          })
        else:
          return jsonify({"active_emotes": {}, "auto_emotes_stats": {}, "total_active": 0, "total_auto": 0})
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/emote-duration/<emote_name>')
    def get_emote_duration(emote_name):
      """API للحصول على مدة رقصة معينة"""
      try:
        if hasattr(bot_instance, 'emote_timing') and bot_instance.emote_timing:
          duration = bot_instance.emote_timing.get_emote_duration(emote_name)
          category = bot_instance.emote_timing.get_emote_type_category(emote_name)
          is_custom = emote_name in bot_instance.emote_timing.custom_durations

          return jsonify({
            "emote_name": emote_name,
            "duration": duration,
            "category": category,
            "is_custom": is_custom,
            "duration_text": f"{duration} ثانية"
          })
        else:
          return jsonify({"error": "مدير التوقيت غير متاح"})
      except Exception as e:
        return jsonify({"error": str(e)})

    @self.app.route('/api/discovered-emotes')
    def get_discovered_emotes():
      """API للحصول على الرقصات المكتشفة حديثاً"""
      try:
        if hasattr(bot_instance, 'emote_timing') and bot_instance.emote_timing:
          # قراءة الرقصات الجديدة من الملف
          import json
          import os

          discovered_emotes = []
          timing_file = bot_instance.emote_timing.timing_file

          if os.path.exists(timing_file):
            with open(timing_file, 'r', encoding='utf-8') as f:
              data = json.load(f)
              new_emotes = data.get("new_emotes", {})

              for emote_name, duration in new_emotes.items():
                discovered_emotes.append({
                  "name": emote_name,
                  "duration": duration,
                  "category": bot_instance.emote_timing.get_emote_type_category(emote_name)
                })

          return jsonify({
            "success": True,
            "discovered_emotes": discovered_emotes,
            "total": len(discovered_emotes)
          })
        else:
          return jsonify({"success": False, "error": "مدير التوقيت غير متاح"})
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/emote-timing')
    def emote_timing_page():
      """صفحة إدارة أوقات الرقصات"""
      return render_template('emote_timing.html')

    @self.app.route('/responses')
    def responses_page():
      """صفحة إدارة الردود التلقائية"""
      return render_template('responses.html')

    @self.app.route('/command-builder')
    def command_builder_page():
      """صفحة مصنع الأوامر المخصصة"""
      return render_template('command_builder.html')

    @self.app.route('/api/verify-command-builder-password', methods=['POST'])
    def verify_command_builder_password():
      """التحقق من كلمة مرور مصنع الأوامر"""
      try:
        data = request.get_json()
        password = data.get('password', '').strip()

        # كلمة المرور المطلوبة
        required_password = "01018"

        if password == required_password:
          # إرسال رسالة للبوت عند فتح مصنع الأوامر بنجاح
          try:
            with open('temp_command.txt', 'w', encoding='utf-8') as f:
              f.write('say 🛠️ تم فتح مصنع الأوامر! الأوامر الجديدة في الطريق... ⚡')
          except Exception as e:
            print(f"❌ فشل في إرسال إشعار البوت: {e}")

          return jsonify({
            "success": True,
            "message": "تم التحقق من كلمة المرور بنجاح"
          })
        else:
          return jsonify({
            "success": False,
            "error": "كلمة المرور غير صحيحة"
          })

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/emote-timings')
    def get_all_emote_timings():
      """API للحصول على جميع أوقات الرقصات"""
      try:
        if hasattr(bot_instance, 'emotes_manager') and hasattr(bot_instance, 'emote_timing'):
          emotes_list = bot_instance.emotes_manager.emotes_list
          timings = bot_instance.emote_timing.get_all_emote_timings(emotes_list)

          return jsonify({
            "success": True,
            "emotes": timings,
            "total_count": len(timings)
          })
        else:
          return jsonify({
            "success": False,
            "error": "مدير الرقصات أو مدير التوقيت غير متاح"
          })
      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/update-emote-timing', methods=['POST'])
    def update_emote_timing():
      """API لتحديث توقيت رقصة واحدة"""
      try:
        if not hasattr(bot_instance, 'emote_timing'):
          return jsonify({
            "success": False,
            "error": "مدير التوقيت غير متاح"
          })

        data = request.get_json()
        emote_name = data.get('emote_name')
        duration = data.get('duration')

        if not emote_name or duration is None:
          return jsonify({
            "success": False,
            "error": "اسم الرقصة والمدة مطلوبان"
          })

        success = bot_instance.emote_timing.update_emote_duration(emote_name, float(duration))

        if success:
          # إرسال رسالة تأكيد للبوت ليرسلها في الغرفة
          confirmation_message = f"⏰ تم تحديث توقيت رقصة {emote_name} إلى {duration} ثانية من الواجهة"
          with open('temp_command.txt', 'w', encoding='utf-8') as f:
            f.write(f'say {confirmation_message}')

          return jsonify({
            "success": True,
            "message": f"تم تحديث توقيت رقصة {emote_name} إلى {duration} ثانية"
          })
        else:
          return jsonify({
            "success": False,
            "error": "فشل في تحديث التوقيت - تأكد من أن المدة بين 0.5 و 60 ثانية"
          })

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/update-all-emote-timings', methods=['POST'])
    def update_all_emote_timings():
      """API لتحديث أوقات متعددة"""
      try:
        if not hasattr(bot_instance, 'emote_timing'):
          return jsonify({
            "success": False,
            "error": "مدير التوقيت غير متاح"
          })

        data = request.get_json()
        emote_timings = data.get('emote_timings', {})

        if not emote_timings:
          return jsonify({
            "success": False,
            "error": "لا توجد أوقات للتحديث"
          })

        updated_count = bot_instance.emote_timing.update_multiple_durations(emote_timings)

        if updated_count > 0:
          # إرسال رسالة تأكيد للبوت ليرسلها في الغرفة
          confirmation_message = f"⏰ تم تحديث أوقات {updated_count} رقصة بنجاح من الواجهة"
          with open('temp_command.txt', 'w', encoding='utf-8') as f:
            f.write(f'say {confirmation_message}')

        return jsonify({
          "success": True,
          "updated_count": updated_count,
          "message": f"تم تحديث {updated_count} رقصة بنجاح"
        })

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/reset-emote-timings', methods=['POST'])
    def reset_emote_timings():
      """API لإعادة تعيين جميع الأوقات للقيم الافتراضية"""
      try:
        if not hasattr(bot_instance, 'emote_timing'):
          return jsonify({
            "success": False,
            "error": "مدير التوقيت غير متاح"
          })

        success = bot_instance.emote_timing.reset_all_durations()

        if success:
          # إرسال رسالة تأكيد للبوت ليرسلها في الغرفة
          confirmation_message = "⏰ تم إعادة تعيين جميع أوقات الرقصات للقيم الافتراضية من الواجهة"
          with open('temp_command.txt', 'w', encoding='utf-8') as f:
            f.write(f'say {confirmation_message}')

          return jsonify({
            "success": True,
            "message": "تم إعادة تعيين جميع أوقات الرقصات للقيم الافتراضية"
          })
        else:
          return jsonify({
            "success": False,
            "error": "فشل في إعادة تعيين الأوقات"
          })

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    # تم حذف APIs القديمة - يتم استخدام execute-command الآن لجميع الأوامر

    # APIs نظام التحديثات
    @self.app.route('/api/check-updates', methods=['GET'])
    def check_updates():
      """فحص التحديثات المتاحة"""
      try:
        updates = self.update_manager.get_available_updates()
        return jsonify({
          "success": True,
          "updates": updates,
          "count": len(updates)
        })
      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/apply-update', methods=['POST'])
    def apply_update():
      """تطبيق تحديث معين - لا يتطلب كود مطور"""
      try:
        data = request.get_json()
        update_id = data.get('update_id')

        if not update_id:
          return jsonify({
            "success": False,
            "error": "معرف التحديث مطلوب"
          })

        # تطبيق التحديث بدون التحقق من كود المطور
        result = self.update_manager.apply_update(update_id)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/upload-update', methods=['POST'])
    def upload_update():
      """رفع تحديث جديد (للمطورين فقط)"""
      try:
        # التحقق من كود المطور
        developer_code = request.form.get('developer_code', '')
        if not self.update_manager.verify_developer_code(developer_code):
          return jsonify({
            "success": False,
            "error": "كود المطور غير صحيح"
          })

        # التحقق من وجود الملف
        if 'update_file' not in request.files:
          return jsonify({
            "success": False,
            "error": "لم يتم رفع ملف"
          })

        file = request.files['update_file']
        if file.filename == '':
          return jsonify({
            "success": False,
            "error": "لم يتم اختيار ملف"
          })

        # الحصول على بيانات التحديث
        version = request.form.get('version', '')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        changelog = request.form.get('changelog', '')

        if not all([version, title]):
          return jsonify({
            "success": False,
            "error": "رقم النسخة والعنوان مطلوبان"
          })

        # حفظ الملف مؤقتاً
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
          file.save(tmp_file.name)

          # رفع التحديث
          result = self.update_manager.upload_update(
            tmp_file.name, version, title, description, changelog
          )

          # حذف الملف المؤقت
          os.unlink(tmp_file.name)

          return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/system-info', methods=['GET'])
    def get_system_info():
      """الحصول على معلومات النظام"""
      try:
        info = self.update_manager.get_system_info()
        return jsonify({
          "success": True,
          "system_info": info
        })
      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/extract-zip', methods=['POST'])
    def extract_zip():
      """فك ضغط ملف ZIP"""
      try:
        data = request.get_json()
        zip_path = data.get('zip_path', '')
        extract_to = data.get('extract_to', None)
        password = data.get('password', None)

        if not zip_path:
          return jsonify({
            "success": False,
            "error": "مسار ملف ZIP مطلوب"
          })

        result = self.update_manager.extract_zip_file(zip_path, extract_to, password)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/create-zip', methods=['POST'])
    def create_zip():
      """إنشاء ملف ZIP"""
      try:
        data = request.get_json()
        source_path = data.get('source_path', '')
        zip_path = data.get('zip_path', '')
        compression_level = data.get('compression_level', 6)

        if not all([source_path, zip_path]):
          return jsonify({
            "success": False,
            "error": "مسار المصدر ومسار ZIP مطلوبان"
          })

        result = self.update_manager.create_zip_file(source_path, zip_path, compression_level)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/list-zip-contents', methods=['POST'])
    def list_zip_contents():
      """عرض محتويات ملف ZIP"""
      try:
        data = request.get_json()
        zip_path = data.get('zip_path', '')

        if not zip_path:
          return jsonify({
            "success": False,
            "error": "مسار ملف ZIP مطلوب"
          })

        result = self.update_manager.list_zip_contents(zip_path)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/extract-specific-files', methods=['POST'])
    def extract_specific_files():
      """استخراج ملفات محددة من ZIP"""
      try:
        data = request.get_json()
        zip_path = data.get('zip_path', '')
        file_patterns = data.get('file_patterns', [])
        extract_to = data.get('extract_to', None)

        if not zip_path or not file_patterns:
          return jsonify({
            "success": False,
            "error": "مسار ZIP وقائمة الأنماط مطلوبة"
          })

        result = self.update_manager.extract_specific_files(zip_path, file_patterns, extract_to)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/validate-zip', methods=['POST'])
    def validate_zip():
      """التحقق من سلامة ملف ZIP"""
      try:
        data = request.get_json()
        zip_path = data.get('zip_path', '')

        if not zip_path:
          return jsonify({
            "success": False,
            "error": "مسار ملف ZIP مطلوب"
          })

        result = self.update_manager.validate_zip_integrity(zip_path)
        return jsonify(result)

      except Exception as e:
        return jsonify({
          "success": False,
          "error": str(e)
        })

    # APIs إدارة الردود التلقائية
    @self.app.route('/api/responses/get', methods=['GET'])
    def get_responses():
      """الحصول على جميع الردود"""
      try:
        from modules.responses_manager import responses_manager
        responses = responses_manager.get_all_responses()
        return jsonify(responses)
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/responses/add', methods=['POST'])
    def add_response():
      """إضافة رسالة جديدة"""
      try:
        from modules.responses_manager import responses_manager
        data = request.get_json()
        user_type = data.get('user_type')
        message = data.get('message')

        print(f"🔄 طلب إضافة رسالة: {user_type} = {message}")

        if not user_type or not message:
          return jsonify({"success": False, "error": "نوع المستخدم والرسالة مطلوبان"})

        # التأكد من أن الرسالة ليست فارغة بعد التنظيف
        message = message.strip()
        if not message:
          return jsonify({"success": False, "error": "الرسالة لا يمكن أن تكون فارغة"})

        success = responses_manager.add_welcome_message(user_type, message)

        if success:
          print(f"✅ تم إضافة رسالة بنجاح لـ {user_type}")
          return jsonify({"success": True, "message": "تم إضافة الرسالة بنجاح"})
        else:
          return jsonify({"success": False, "error": "فشل في إضافة الرسالة أو الرسالة موجودة مسبقاً"})

      except Exception as e:
        print(f"❌ خطأ في إضافة الرسالة: {e}")
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/responses/remove', methods=['POST'])
    def remove_response():
      """حذف رسالة"""
      try:
        from modules.responses_manager import responses_manager
        data = request.get_json()
        user_type = data.get('user_type')
        index = data.get('index')

        if user_type is None or index is None:
          return jsonify({"success": False, "error": "نوع المستخدم والفهرس مطلوبان"})

        # الحصول على الرسالة للحذف
        responses = responses_manager.get_all_responses()
        messages = responses.get("welcome_responses", {}).get(user_type, [])

        if 0 <= index < len(messages):
          message = messages[index]
          success = responses_manager.remove_welcome_message(user_type, message)
          return jsonify({"success": success})
        else:
          return jsonify({"success": False, "error": "فهرس غير صحيح"})
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/responses/toggle-welcome', methods=['POST'])
    def toggle_welcome():
      """تفعيل/إيقاف الردود الترحيبية"""
      try:
        from modules.responses_manager import responses_manager
        new_state = responses_manager.toggle_welcome()
        return jsonify({"success": True, "enabled": new_state})
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/responses/toggle-farewell', methods=['POST'])
    def toggle_farewell():
      """تفعيل/إيقاف الردود الوداعية"""
      try:
        from modules.responses_manager import responses_manager
        new_state = responses_manager.toggle_farewell()
        return jsonify({"success": True, "enabled": new_state})
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    # APIs الأوامر المخصصة
    @self.app.route('/api/custom-commands', methods=['GET'])
    def get_custom_commands_api():
      """الحصول على الأوامر المخصصة"""
      try:
        from modules.custom_commands_manager import custom_commands_manager
        all_commands = custom_commands_manager.commands_data
        return jsonify({
          "success": True,
          "commands": all_commands,
          "stats": custom_commands_manager.get_stats()
        })
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/custom-commands/add', methods=['POST'])
    def add_custom_command():
      """API لإضافة أمر مخصص جديد"""
      try:
        data = request.get_json()
        command = data.get('command', '').strip()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        z = float(data.get('z', 0))  
        message = data.get('message', '').strip()
        permissions = data.get('permissions', 'everyone')

        # تجميع الإحداثيات في متغير واحد
        coordinates = {
          'x': x,
          'y': y,
          'z': z
        }

        from modules.custom_commands_manager import custom_commands_manager
        success, result = custom_commands_manager.add_navigation_command(
          command, coordinates, message, permissions
        )

        # إرسال إشعار للبوت في حالة النجاح
        if success:
          try:
            with open('temp_command.txt', 'w', encoding='utf-8') as f:
              f.write(f'say ✅ تم إنشاء أمر التنقل "{command}" بنجاح! 🎯')
          except Exception as e:
            print(f"❌ فشل في إرسال إشعار البوت: {e}")

        return jsonify({"success": success, "message": result})

      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/custom-commands/add-dance', methods=['POST'])
    def add_dance_command():
      """API لإضافة أمر رقصة مخصص جديد"""
      try:
        data = request.get_json()
        command = data.get('command', '').strip()
        emote = data.get('emote', '').strip()
        message = data.get('message', '').strip()
        permissions = data.get('permissions', 'everyone')

        print(f"🎭 طلب إنشاء أمر رقصة: {command} -> {emote}")

        if not command or not emote:
          return jsonify({"success": False, "error": "كلمة الأمر والرقصة مطلوبة"})

        # إذا لم يتم إدخال رسالة، استخدم رسالة افتراضية
        if not message:
            message = "🕺💃"

        from modules.custom_commands_manager import custom_commands_manager
        success, result = custom_commands_manager.add_dance_command(
          command, emote, message, permissions
        )

        if success:
          print(f"✅ تم إنشاء أمر الرقصة '{command}' بنجاح")
        else:
          print(f"❌ فشل في إنشاء أمر الرقصة '{command}': {result}")

        return jsonify({"success": success, "message": result})

      except Exception as e:
        print(f"❌ خطأ في API إضافة أمر الرقصة: {e}")
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/custom-commands/delete', methods=['POST'])
    def delete_custom_command():
        """حذف أمر مخصص"""
        try:
            data = request.get_json()
            command_id = data.get('id')
            command_type = data.get('type', 'navigation')

            from modules.custom_commands_manager import custom_commands_manager
            success, result = custom_commands_manager.delete_command(command_id, command_type)

            return jsonify({
                'success': success,
                'message': result
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'خطأ في حذف الأمر: {str(e)}'
            }), 500

    @self.app.route('/api/custom-commands/make-auto-repeat', methods=['POST'])
    def make_auto_repeat_command():
        """جعل أمر الرقصة تلقائياً ومتكرراً"""
        try:
            data = request.get_json()
            command = data.get('command')
            emote = data.get('emote')
            command_type = data.get('type', 'dance')

            if not command or not emote:
                return jsonify({
                    'success': False,
                    'error': 'يجب تقديم اسم الأمر والرقصة'
                }), 400

            # تحديث الأمر في مدير الأوامر المخصصة
            from modules.custom_commands_manager import custom_commands_manager
            success, message = custom_commands_manager.make_command_auto_repeat(command, emote)

            return jsonify({
                'success': success,
                'message': message
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'خطأ في تحديث الأمر: {str(e)}'
            }), 500

    @self.app.route('/api/custom-commands/delete-old', methods=['POST'])
    def delete_custom_command_old():
      """حذف أمر مخصص - الطريقة القديمة"""
      try:
        from modules.custom_commands_manager import custom_commands_manager
        data = request.get_json()
        command_id = data.get('id')

        if command_id is None:
          return jsonify({"success": False, "error": "معرف الأمر مطلوب"})

        success, message = custom_commands_manager.delete_navigation_command(command_id)
        return jsonify({"success": success, "message": message})

      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/save-custom-command', methods=['POST'])
    def save_custom_command():
      """حفظ أمر مخصص جديد"""
      try:
        data = request.get_json()

        # التحقق من البيانات المطلوبة
        if not data.get('name') or not data.get('trigger'):
          return jsonify({"success": False, "error": "اسم الأمر وكلمة التشغيل مطلوبان"})

        # إنشاء معرف فريد للأمر
        command_id = f"custom_{int(time.time())}"
        command_data = {
          "id": command_id,
          "name": data['name'],
          "trigger": data['trigger'],
          "permission": data.get('permission', 'all'),
          "description": data.get('description', ''),
          "steps": data.get('steps', []),
          "created_date": datetime.now().isoformat(),
          "active": True
        }

        # تحميل الأوامر المحفوظة
        commands_file = 'data/custom_commands.json'
        if os.path.exists(commands_file):
          with open(commands_file, 'r', encoding='utf-8') as f:
            commands = json.load(f)
        else:
          commands = []

        # إضافة الأمر الجديد
        commands.append(command_data)

        # حفظ الملف
        os.makedirs(os.path.dirname(commands_file), exist_ok=True)
        with open(commands_file, 'w', encoding='utf-8') as f:
          json.dump(commands, f, ensure_ascii=False, indent=2)

        # كتابة أمر لإعادة تحميل الأوامر المخصصة في البوت
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write('reload_custom_commands')

        return jsonify({
          "success": True, 
          "message": f"تم حفظ الأمر '{data['name']}' بنجاح",
          "command_id": command_id
        })

      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/get-custom-commands', methods=['GET'])
    def get_all_custom_commands():
      """الحصول على جميع الأوامر المخصصة"""
      try:
        commands_file = 'data/custom_commands.json'
        if os.path.exists(commands_file):
          with open(commands_file, 'r', encoding='utf-8') as f:
            commands_data = json.load(f)
          return jsonify(commands_data)
        else:
          return jsonify({"navigation_commands": [], "message": "لا توجد أوامر مخصصة"})
      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/create-navigation-command', methods=['POST'])
    def create_navigation_command():
      """إنشاء أمر تنقل جديد"""
      try:
        data = request.get_json()
        command = data.get('command', '').strip()
        coordinates = data.get('coordinates', {})
        message = data.get('message', '').strip()
        permissions = data.get('permissions', 'everyone')

        # التحقق من البيانات
        if not command:
          return jsonify({"success": False, "error": "كلمة الأمر مطلوبة"})

        if not all(key in coordinates for key in ['x', 'y', 'z']):
          return jsonify({"success": False, "error": "الإحداثيات غير مكتملة"})

        # استخدام رسالة افتراضية في حالة عدم وجود رسالة
        if not message:
            message = f"تم النقل إلى {command} 📍"

        # تحديد ملف الأوامر
        commands_file = 'data/custom_commands.json'

        # قراءة الأوامر الحالية أو إنشاء ملف جديد
        if os.path.exists(commands_file):
          with open(commands_file, 'r', encoding='utf-8') as f:
            commands_data = json.load(f)
        else:
          commands_data = {"navigation_commands": []}

        # التحقق من عدم وجود أمر بنفس الاسم
        for existing_command in commands_data.get("navigation_commands", []):
          if existing_command.get("command") == command:
            return jsonify({"success": False, "error": f"الأمر '{command}' موجود بالفعل"})

        # إضافة الأمر الجديد
        new_command = {
          "command": command,
          "coordinates": coordinates,
          "message": message,
          "permissions": permissions,
          "created_at": datetime.now().isoformat(),
          "type": "navigation"
        }

        if "navigation_commands" not in commands_data:
          commands_data["navigation_commands"] = []

        commands_data["navigation_commands"].append(new_command)

        # حفظ الملف
        with open(commands_file, 'w', encoding='utf-8') as f:
          json.dump(commands_data, f, ensure_ascii=False, indent=2)

        return jsonify({
          "success": True, 
          "message": f"تم إنشاء أمر التنقل '{command}' بنجاح",
          "command": new_command
        })

      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/test-command', methods=['POST'])
    def test_command():
      """اختبار أمر مخصص"""
      try:
        data = request.get_json()
        trigger = data.get('trigger')
        steps = data.get('steps', [])

        if not trigger:
          return jsonify({"success": False, "error": "كلمة التشغيل مطلوبة"})

        # إنشاء أمر اختبار مؤقت
        test_command = f"test_command:{trigger}"

        # كتابة الأمر للاختبار
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(test_command)

        return jsonify({
          "success": True, 
          "message": f"تم إرسال أمر الاختبار '{trigger}' للبوت"
        })

      except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    @self.app.route('/api/apply-local-update', methods=['POST'])
    def apply_local_update():
      """تطبيق تحديث محلي من ملف رفعه المستخدم مع تحليل متقدم"""
      try:
        # التحقق من وجود الملف
        if 'update_file' not in request.files:
          return jsonify({
            "success": False,
            "error": "لم يتم رفع ملف"
          })

        file = request.files['update_file']
        if file.filename == '':
          return jsonify({
            "success": False,
            "error": "لم يتم اختيار ملف"
          })

        # التحقق من نوع الملف
        if not file.filename.lower().endswith('.zip'):
          return jsonify({
            "success": False,
            "error": "يجب أن يكون الملف بصيغة ZIP"
          })

        # حفظ الملف مؤقتاً
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
          file.save(tmp_file.name)

          # التحقق من صحة الملف
          if not zipfile.is_zipfile(tmp_file.name):
            os.unlink(tmp_file.name)
            return jsonify({
              "success": False,
              "error": "الملف ليس ملف ZIP صحيح"
            })

          # إنشاء نسخة احتياطية
          backup_result = self.update_manager.create_backup()
          if not backup_result["success"]:
            os.unlink(tmp_file.name)
            return jsonify({
              "success": False,
              "error": f"فشل في إنشاء النسخة الاحتياطية: {backup_result['error']}"
            })

          # تطبيق التحديث مع التحليل المتقدم
          update_result = self.update_manager.extract_and_apply_update(tmp_file.name)

          # حذف الملف المؤقت
          os.unlink(tmp_file.name)

          if not update_result["success"]:
            # استعادة النسخة الاحتياطية في حالة الفشل
            self.update_manager.restore_backup(backup_result["backup_path"])
            return jsonify({
              "success": False,
              "error": f"فشل في تطبيق التحديث: {update_result['error']}"
            })

          # تسجيل التحديث المحلي مع تفاصيل التحليل
          current_time = datetime.now().isoformat()
          local_update_data = {
            "id": f"local_update_{int(datetime.now().timestamp())}",
            "version": "محلي",
            "source": "ملف محلي من المستخدم",
            "filename": file.filename,
            "applied_date": current_time,
            "backup_path": backup_result["backup_path"],
            "analysis": update_result.get("summary", {}),
            "report": update_result.get("report", "")
          }

          # إضافة التحديث المحلي لسجل التحديثات المطبقة
          if "installed_updates" not in self.update_manager.updates_data:
            self.update_manager.updates_data["installed_updates"] = []

          self.update_manager.updates_data["installed_updates"].append(local_update_data)
          self.update_manager.save_updates_data()

          print(f"✅ تم تطبيق تحديث محلي من الملف: {file.filename}")

          # إرسال تحليل التحديث للبوت ليعرضه في الغرفة
          if update_result.get("report"):
            with open('temp_command.txt', 'w', encoding='utf-8') as f:
              f.write(f'say ✅ تم تطبيق التحديث بنجاح!\n{update_result["report"]}')

          return jsonify({
            "success": True,
            "message": f"تم تطبيق التحديث المحلي من الملف {file.filename} بنجاح",
            "filename": file.filename,
            "backup_path": backup_result["backup_path"],
            "analysis": update_result.get("summary", {}),
            "report": update_result.get("report", "")
          })

      except Exception as e:
        print(f"❌ خطأ في تطبيق التحديث المحلي: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/api/extract-and-analyze', methods=['POST'])
    def extract_and_analyze():
      """فك ضغط وتحليل ملف ZIP دون تطبيق التحديث"""
      try:
        # التحقق من وجود الملف
        if 'zip_file' not in request.files:
          return jsonify({
            "success": False,
            "error": "لم يتم رفع ملف"
          })

        file = request.files['zip_file']
        if file.filename == '':
          return jsonify({
            "success": False,
            "error": "لم يتم اختيار ملف"
          })

        # التحقق من نوع الملف
        if not file.filename.lower().endswith('.zip'):
          return jsonify({
            "success": False,
            "error": "يجب أن يكون الملف بصيغة ZIP"
          })

        # حفظ الملف مؤقتاً
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
          file.save(tmp_file.name)

          # التحقق من صحة الملف
          if not zipfile.is_zipfile(tmp_file.name):
            os.unlink(tmp_file.name)
            return jsonify({
              "success": False,
              "error": "الملف ليس ملف ZIP صحيح"
            })

          # فك الضغط لمجلد مؤقت
          extract_dir = f"temp_extract_{int(time.time())}"
          result = self.update_manager.extract_zip_file(tmp_file.name, extract_dir)

          # حذف الملف المؤقت
          os.unlink(tmp_file.name)

          if not result["success"]:
            return jsonify({
              "success": False,
              "error": f"فشل في فك الضغط: {result.get('error', 'خطأ غير معروف')}"
            })

          # تحليل الملفات المستخرجة
          analysis_summary = {
            "new_files": [],
            "updated_files": [],
            "new_features": [],
            "changes_detected": []
          }

          # تحليل محتويات التحديث
          self.update_manager._analyze_update_contents(extract_dir, analysis_summary)

          # تنظيف المجلد المؤقت
          import shutil
          if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)

          return jsonify({
            "success": True,
            "filename": file.filename,
            "files_extracted": result.get("files_extracted", 0),
            "analysis": analysis_summary,
            "report": self.update_manager._format_update_summary(analysis_summary)
          })

      except Exception as e:
        print(f"❌ خطأ في فك الضغط والتحليل: {e}")
        return jsonify({
          "success": False,
          "error": str(e)
        })

    @self.app.route('/alive')
    def alive() -> str:
      return "Alive"


    @self.app.route('/outfit-creator')
    def outfit_creator():
        """صفحة صانع الملابس"""
        return render_template('outfit_creator.html')

    @self.app.route('/api/test-outfit', methods=['POST'])
    async def test_outfit():
        """API لاختبار الزي"""
        try:
            data = request.get_json()
            codes = data.get('codes', [])

            if not codes:
                return jsonify({'success': False, 'error': 'لا توجد أكواد للاختبار'})

            # إنشاء قائمة قطع الملابس
            from highrise.models import Item
            outfit_items = []
            background_id = None

            for code in codes:
                if code.startswith('bg-'):
                    background_id = code
                else:
                    outfit_items.append(Item(
                        type='clothing',
                        amount=1,
                        id=code,
                        account_bound=False,
                        active_palette=-1
                    ))

            # تطبيق الزي على البوت
            # Ensure bot_instance is available and has highrise attribute
            if hasattr(bot_instance, 'highrise'):
                result = await bot_instance.highrise.set_outfit(outfit=outfit_items)

                # تطبيق الخلفية إذا وجدت
                if background_id:
                    try:
                        if hasattr(bot_instance.highrise, 'set_backdrop'):
                            await bot_instance.highrise.set_backdrop(background_id)
                        elif hasattr(bot_instance.highrise, 'set_room_backdrop'):
                            await bot_instance.highrise.set_room_backdrop(background_id)
                    except Exception as bg_error:
                        print(f"فشل في تطبيق الخلفية: {bg_error}")

                return jsonify({
                    'success': True,
                    'message': f'تم تطبيق الزي بنجاح! ({len(outfit_items)} قطعة)',
                    'applied_pieces': len(outfit_items),
                    'has_background': background_id is not None
                })
            else:
                 return jsonify({'success': False, 'error': 'Highrise instance not available.'})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @self.app.route('/api/save-outfit', methods=['POST'])
    def save_outfit():
      """حفظ زي جديد"""
      try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        codes = data.get('codes', [])
        developer = data.get('developer', 'مجهول')

        if not name:
          return jsonify({'success': False, 'error': 'اسم الزي مطلوب'})

        if not codes:
          return jsonify({'success': False, 'error': 'أكواد الملابس مطلوبة'})

        # إنشاء معرف فريد للزي
        import uuid
        outfit_id = str(uuid.uuid4())

        # تحميل الأزياء الحالية
        outfits_file = 'data/outfits_data.json'
        outfits_data = {}

        if os.path.exists(outfits_file):
          with open(outfits_file, 'r', encoding='utf-8') as f:
            outfits_data = json.load(f)

        # إضافة الزي الجديد
        new_outfit = {
          'id': outfit_id,
          'name': name,
          'description': description,
          'codes': codes,
          'created_by': developer,
          'created_at': datetime.now().isoformat(),
          'category': 'custom',
          'total_pieces': len(codes)
        }

        outfits_data[outfit_id] = new_outfit

        # حفظ البيانات
        os.makedirs('data', exist_ok=True)
        with open(outfits_file, 'w', encoding='utf-8') as f:
          json.dump(outfits_data, f, ensure_ascii=False, indent=2)

        return jsonify({
          'success': True,
          'message': f'تم حفظ الزي "{name}" بنجاح',
          'outfit_id': outfit_id,
          'total_pieces': len(codes)
        })

      except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    @self.app.route('/api/save-bot-current-outfit', methods=['POST'])
    def save_bot_current_outfit():
      """حفظ الزي الحالي للبوت"""
      try:
        # إرسال أمر للبوت لحفظ الزي الحالي
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write('save_current_outfit')

        return jsonify({
          'success': True,
          'message': 'تم إرسال أمر حفظ الزي للبوت'
        })

      except Exception as e:
        print(f"خطأ في حفظ الزي: {e}")
        return jsonify({
          'success': False,
          'error': str(e)
        })

    @self.app.route('/api/save-outfit-with-name', methods=['POST'])
    def save_outfit_with_name():
      """حفظ الزي الحالي مع اسم مخصص"""
      try:
        data = request.get_json()
        outfit_name = data.get('name', '').strip()
        outfit_description = data.get('description', '').strip()

        if not outfit_name:
          return jsonify({
            'success': False,
            'error': 'اسم الزي مطلوب'
          })

        # إرسال أمر للبوت لحفظ الزي مع الاسم
        command = f'save_outfit_named:{outfit_name}:{outfit_description}'
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(command)

        return jsonify({
          'success': True,
          'message': f'تم إرسال أمر حفظ الزي "{outfit_name}" للبوت'
        })

      except Exception as e:
        print(f"خطأ في حفظ الزي المسمى: {e}")
        return jsonify({
          'success': False,
          'error': str(e)
        })

    @self.app.route('/api/saved-outfits', methods=['GET'])
    def get_saved_outfits():
      """الحصول على قائمة الأزياء المحفوظة"""
      try:
        outfits_file = 'data/saved_outfits.json'
        if os.path.exists(outfits_file):
          with open(outfits_file, 'r', encoding='utf-8') as f:
            outfits_data = json.load(f)
        else:
          outfits_data = {}

        # تحويل البيانات لتنسيق مناسب للعرض
        outfits_list = []
        for outfit_id, outfit_info in outfits_data.items():
          outfits_list.append({
            'id': outfit_id,
            'name': outfit_info.get('name', 'زي بدون اسم'),
            'description': outfit_info.get('description', ''),
            'saved_at': outfit_info.get('saved_at', ''),
            'total_items': outfit_info.get('total_items', 0),
            'preview_items': outfit_info.get('items_list', [])[:5]  # أول 5 قطع للمعاينة
          })

        # ترتيب حسب تاريخ الحفظ (الأحدث أولاً)
        outfits_list.sort(key=lambda x: x['saved_at'], reverse=True)

        return jsonify({
          'success': True,
          'outfits': outfits_list,
          'total_count': len(outfits_list)
        })

      except Exception as e:
        print(f"خطأ في جلب الأزياء المحفوظة: {e}")
        return jsonify({
          'success': False,
          'error': str(e),
          'outfits': []
        })

    @self.app.route('/api/apply-saved-outfit', methods=['POST'])
    def apply_saved_outfit():
      """تطبيق زي محفوظ"""
      try:
        data = request.get_json()
        outfit_id = data.get('outfit_id', '').strip()

        if not outfit_id:
          return jsonify({
            'success': False,
            'error': 'معرف الزي مطلوب'
          })

        # إرسال أمر للبوت لتطبيق الزي المحفوظ
        command = f'apply_saved_outfit:{outfit_id}'
        with open('temp_command.txt', 'w', encoding='utf-8') as f:
          f.write(command)

        return jsonify({
          'success': True,
          'message': 'تم إرسال أمر تطبيق الزي المحفوظ للبوت'
        })

      except Exception as e:
        print(f"خطأ في تطبيق الزي المحفوظ: {e}")
        return jsonify({
          'success': False,
          'error': str(e)
        })

    @self.app.route('/api/delete-saved-outfit', methods=['POST'])
    def delete_saved_outfit():
      """حذف زي محفوظ"""
      try:
        data = request.get_json()
        outfit_id = data.get('outfit_id', '').strip()

        if not outfit_id:
          return jsonify({
            'success': False,
            'error': 'معرف الزي مطلوب'
          })

        outfits_file = 'data/saved_outfits.json'
        if os.path.exists(outfits_file):
          with open(outfits_file, 'r', encoding='utf-8') as f:
            outfits_data = json.load(f)

          if outfit_id in outfits_data:
            outfit_name = outfits_data[outfit_id].get('name', 'زي بدون اسم')
            del outfits_data[outfit_id]

            # حفظ البيانات المحدثة
            with open(outfits_file, 'w', encoding='utf-8') as f:
              json.dump(outfits_data, f, ensure_ascii=False, indent=2)

            return jsonify({
              'success': True,
              'message': f'تم حذف الزي "{outfit_name}" بنجاح'
            })
          else:
            return jsonify({
              'success': False,
              'error': 'الزي غير موجود'
            })
        else:
          return jsonify({
            'success': False,
            'error': 'لا توجد أزياء محفوظة'
          })

      except Exception as e:
        print(f"خطأ في حذف الزي المحفوظ: {e}")
        return jsonify({
          'success': False,
          'error': str(e)
        })

  def run(self) -> None:
    self.app.run(host='0.0.0.0', port=8080)

  def keep_alive(self):
    t = Thread(target=self.run)
    t.start()


class RunBot():
  def __init__(self) -> None:
    # البيانات الثابتة - غير هذه القيم حسب بياناتك
    self.room_id = "68068acfda361bbd9bcae760"  # معرف الغرفة الجديد
    self.bot_token = "4185d3da2015013be900077c1e2874ad7d83e6e6f76ecd91cf96ce4104d9d6ff"  # توكن البوت - ضع توكن البوت الخاص بك هنا

    self.bot_file = "main"
    self.main_bot_class = "MyBot"

    self.definitions = [
        # البوت الرئيسي فقط
        BotDefinition(
            getattr(import_module(self.bot_file), self.main_bot_class)(),
            self.room_id, self.bot_token),
    ]
    global bot_instance
    bot_instance = self.definitions[0].bot

  def run_loop(self) -> None:
    consecutive_errors = 0
    max_consecutive_errors = 10

    while consecutive_errors < max_consecutive_errors:
      try:
        arun(main(self.definitions))
        consecutive_errors = 0  # إعادة تعيين العداد عند النجاح

      except Exception as e:
        consecutive_errors += 1
        error_str = str(e).lower()

        # معالجة خاصة لأخطاء الاتصال والـ Multilogin
        if "transport" in error_str or "connection" in error_str or "multilogin" in error_str:
          print(f"🔄 مشكلة اتصال ({consecutive_errors}/{max_consecutive_errors}): {e}")

          # في حالة Multilogin، انتظار أطول
          if "multilogin" in error_str:
            sleep_time = min(60 + (consecutive_errors * 30), 300)  # انتظار أطول للـ Multilogin
            print(f"⚠️ خطأ Multilogin - انتظار {sleep_time} ثانية لحل التضارب...")
          else:
            sleep_time = min(30 + (consecutive_errors * 10), 120)
            print(f"⏳ إعادة المحاولة خلال {sleep_time} ثانية...")

          time.sleep(sleep_time)
        else:
          # Print the full traceback for other exceptions
          import traceback
          print("Caught an exception:")
          traceback.print_exc()
          print(f"إعادة المحاولة خلال 10 ثوانِ... (محاولة {consecutive_errors})")
          time.sleep(10)
        continue

    print("❌ تم الوصول للحد الأقصى من الأخطاء المتتالية. إيقاف البوت.")
    print("💡 يرجى التحقق من حالة الشبكة وإعادة تشغيل البوت يدوياً.")


if __name__ == "__main__":
  WebServer().keep_alive()

  bot = RunBot()
  RunBot().run_loop()
from highrise import User
from highrise.models import Item

async def on_user_join(self, user: User) -> None:
        """عند دخول مستخدم جديد للغرفة مع فحص متقدم للصلاحيات"""
        try:
            # إضافة المستخدم لقاعدة البيانات مع فحص متقدم
            user_info = await self.user_manager.add_user_to_room(user, self)

            print(f"👋 {user.username} دخل الغرفة")
            print(f"   📊 النوع: {user_info['user_type']}")
            print(f"   👮‍♂️ مشرف: {user_info['is_moderator']}")

            # رسالة ترحيب حسب نوع المستخدم
            welcome_msg = self.responses_manager.get_welcome_response(user)
            if welcome_msg:
                await self.highrise.chat(welcome_msg)

        except Exception as e:
            print(f"❌ خطأ في معالجة دخول المستخدم {user.username}: {e}")
import telebot
import dropbox
import time
import os
from flask import Flask
from threading import Thread

# Tokens
BOT_TOKEN = "9285811920:AAF-aBN-XIa76Le876ij2YctE64CpX-76DE"
ADMIN_ID = 998367745
DROPBOX_TOKEN = "sl.u.AG4l7JIjqUOijSa0OJVMD5dAD4PvDgXZZFgvphc1l5SGXLW8XiqFSVBnHfqSt4MXvRlyekOf1Pf_fANPQB5Ie1beqk6lIaMkt8Za7supjTsGiFABY5mMBFJ3Ukrh0HUPF-9pjry6dKWEfo5vQ5iICfY9AOvvagYdi-OVP5PvxQztKFeuxnq5DQ6G0ETK_tXor9hVw7PZxfE42yazFCo4AXhOmi57CcsOUyodJR6WnythA2SUOBaZQEuKc3vVAPjbiMK-ijfFlTBrMClTnabAMwUyzn3fhQvw39vefQfLtN1yy0PjU8H5GI6w41mitvHLule8C2eCVRjUtEnnDEIAsvvS6s73BfHOY5ZMzCu3RP9wMtdrlcE5TPP6RSLMi4SIFJCcdAWMp81rvE27sXgSaorL-Cbl8Tse2ul9P5z26IM9Um_dYv9UWY2HGhLK1yaEk4GAhmrweEczsDtboWa7ap3m1xCMvCai43z7sWbcBPVG8ES5jK5w8eH6MKDzcD3hjrMLQekAePhB2G_H4lVtzxDFqrzS82Q5nK8imAs20r_tgXENMr8MC3nL9Sg_kWnlAkF31oAMPnJhKKIoUpRLkSeucxUzYw2z_Spo_lBJwHTTg8CH1mUv92x0hN85Pi6Z3blM19HlJBcYJWV2Ic4RyF9ealh6GwcpdqJs_pvsar7uUHRbPNCe2EspCtdt6NeGkkeaI5mkxWx0BEYtgJjgyBRrftAFiPMzexVkOfT4c_zdAESr_Ja-OIlxURZ123sMQfNtQEn-0ajBwmBrWLu0bDGurnliGATmOl7TcvjCYCrzaDoyQxNRco1vDOc8YaQTl6RLgtSkkMb0Vqp2Bcku3HS_EW0mnAM5juZvR5hsg1l7rL3BVPAJGuo84mQ5DWNVBhupr3N0-lmFLVLvT3Z7FcGV6KQ7PAIHkIdfdpawAY1Y9Ndu4YfjpIr6VWL2fTX8-IPBBC9OnTymn5wuMkLFt30Us7nQ_nmQqDqT2iYk70Ox9uet73bbCWWdyAks86a8kQMkiAwPVT0-WqksoUsnA-P4bec0gMviKj-cnAQ4Ks3IKUsupYAUuiSQutTyXnA8h8WlrVBdKR2xHyJ3dKLmJCntKR1wRX8Gh8bmGXMv6B0MokDpWJ0R9-Y8eMYlouk29nG0alOcvGRjHQttaVGSVggCa4pzL6W-iaKEQZYKL0SBB1ktWjh4PoZFz5RxpTOcZbxhK3I4-zPY_OVyhw0Yw619fXloeNEKb4w8wKRSDyODIn5hXrzkI-QaqYUb10aj-0XsqkCTSKjHhSvzFET6__QTxV4ODL6_EIdiXFJlIh_fKH9XsB6Gq2eRMInKGpgjYYNFqxwW_0kK2bJsWOs8FuSfdNSxoS-uotYhetbt3G6kMPrWnpzkzzO1hjAAQ442qdaMsl3pmHqScD_q5aPS4GbudBvaBp3n8j9wAKx9Cfqor8PnTdLkZbty82PjC6JRllA5GgxG8v5hTPPEGF_ZHN-w"

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# UptimeRobot ke liye ek chota sa web page
@app.route('/')
def home():
    return "✅ Bhumi VIP Dropbox Bot is ALIVE and RUNNING!"

def run_server():
    # Render cloud ke liye 0.0.0.0 zaroori hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@bot.message_handler(content_types=['video', 'document'])
def handle_video(message):
    if message.chat.id != ADMIN_ID: return
        
    msg = bot.reply_to(message, "⏳ Bhumi Dropbox VIP Link nikal rahi hai... Wait babu...")
    try:
        file_id = message.video.file_id if message.content_type == 'video' else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        local_filename = f"temp_{int(time.time())}.mp4"
        with open(local_filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        dropbox_path = f"/{int(time.time())}_reel.mp4"
        with open(local_filename, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
        
        try:
            shared_link_meta = dbx.sharing_create_shared_link_with_settings(dropbox_path)
            raw_url = shared_link_meta.url
        except dropbox.exceptions.ApiError as err:
            if err.error.is_shared_link_already_exists():
                raw_url = err.error.get_shared_link_already_exists().metadata.url
            else:
                raise err
                
        vip_direct_url = raw_url.replace("?dl=0", "?raw=1").replace("&dl=0", "&raw=1")
        
        bot.edit_message_text(f"✅ Ye le babu, Bhumi ki 100% Meta-Ready ?raw=1 Link:\n\n{vip_direct_url}", chat_id=message.chat.id, message_id=msg.message_id)
        os.remove(local_filename)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error aagaya babu: {e}", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == "__main__":
    # Web server ko alag thread me start kiya
    server_thread = Thread(target=run_server)
    server_thread.start()
    print("👩‍💻 Flask Server Running... Starting Telegram Bot...")
    # Bot ko main thread me run kiya
    bot.polling(none_stop=True)

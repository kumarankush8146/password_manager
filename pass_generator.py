import random,bcrypt,sqlite3,os,base64
from sqlite3 import Error
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from prettytable import PrettyTable

def generate_password():
    choices= "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()/\~`[]"
    rand_password = [random.choice(choices) for i in range(25)] 
    rand_password = "".join(rand_password)
    return rand_password.encode()

def sql_connection():

    try:

        conn = sqlite3.connect('main.db')

        return conn

    except Error:

        print(Error)

def Insert(conn, a):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO PERSONAL (USERNAME,WEBSITE,PASSWORD) VALUES(?,?,?)",a)
        conn.commit()

    except Error:

        print(Error)

    finally:

        conn.close()

    # unhashed_passw= a.encode('utf-8') 
    # hashed_passw = bcrypt.hashpw(unhashed_passw,bcrypt.gensalt())
def Show(master_key,conn):
    try:
        cur = conn.cursor()
        data = cur.execute("SELECT * from PERSONAL WHERE ID>1")
        print("Your Existing Details are:")
        t = PrettyTable(['ID', 'USERNAME','SITE','PASSWORD'])
        for row in data:
           t.add_row([row[0],row[1],row[2],decrypt(master_key,row[3])])
       
        print(t)
    except Error:

        print(Error)

    finally:

        conn.close()



def encryption(master_key,user_password):
    #we will get this main pass form data base
    salt = b'\xd0O\xb3\xeb\xa7\x87\x8dg!\x93\xf7\\\xd5\xb0\x15\xd6'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,salt=salt,iterations=100000,backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    user_password = user_password
    f= Fernet(key)
    encrypted = f.encrypt(user_password)
    return encrypted

def decrypt(master_key,encrypted_pass):
    salt = b'\xd0O\xb3\xeb\xa7\x87\x8dg!\x93\xf7\\\xd5\xb0\x15\xd6'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,salt=salt,iterations=100000,backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    f= Fernet(key)
    decrypted = f.decrypt(encrypted_pass)
    return decrypted.decode()

def main():
    print("1. Generate New Password")
    print("2. Show My Saved Passwords")
    a = int(input("Enter Your Choice: "))

    if (a==1):
        global master_key
        master_key = input("Enter your master-key: ")
        conn = sql_connection()
        cur= conn.cursor()
        cur.execute("SELECT PASSWORD FROM PERSONAL WHERE ID=1")
        hashed=cur.fetchone()[0]
        
        if bcrypt.checkpw(master_key.encode(),hashed.encode()):
            temp_username = input("Enter Username: ")
            temp_site = input("Enter Site: ")
            passw = generate_password() #random generated password
            temp = encryption(master_key,passw)
            items = (temp_username,temp_site,temp)
            print("Your Password is:",passw.decode())
            print("ADDING TO DATABASE")
            Insert(conn, items) #adding element to db
            print("Done! Please Copy your password")
        
        else :
            print("Enter Valid Password!")
        
    elif (a==2):
        master_key = input("Enter your master-key: ")
        conn =sql_connection()
        cur= conn.cursor()
        cur.execute("SELECT PASSWORD FROM PERSONAL WHERE ID=1")
        hashed=cur.fetchone()[0]
        if bcrypt.checkpw(master_key.encode(),hashed.encode()):
            Show(master_key,conn)
        else:
            print("Enter valid Password")

    else:
        print("Enter valid choice")

    exit = input('Want to stay on the application?(y/n) ')
    if exit == 'y':
        main()

if __name__ == '__main__':
    main()

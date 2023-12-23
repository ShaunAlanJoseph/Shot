import os
import base64
from cryptography.fernet import Fernet
import custom_string_functions as csf

def generate_key():
  key = Fernet.generate_key()
  key = base64.urlsafe_b64encode(key).decode('utf-8')
  return key

def decrypt(encrypted, key = ""):
  if not key:
    key = os.environ["CONFIG_ENCRYPTION_KEY"]
  key = base64.urlsafe_b64decode(key)
  encrypted = base64.urlsafe_b64decode(encrypted)
  fernet = Fernet(key)
  decrypted = fernet.decrypt(encrypted).decode("utf-8")
  return decrypted

def encrypt(decrypted, key = ""):
  if not key:
    key = os.environ["CONFIG_ENCRYPTION_KEY"]
  key = base64.urlsafe_b64decode(key)
  fernet = Fernet(key)
  encrypted = fernet.encrypt(decrypted.encode("utf-8"))
  encrypted = base64.b64encode(encrypted).decode('utf-8')
  return encrypted

def encrypted_file_read(file, key = ""):
  if not key:
    key = os.environ["CONFIG_ENCRYPTION_KEY"]
  file = open(file, "r")
  file_data = file.read()
  file.close()
  file_data = decrypt(file_data, key)
  return file_data

def encrypted_file_write(file, file_data, key = ""):
  if not key:
    key = os.environ["CONFIG_ENCRYPTION_KEY"]
  file_data = encrypt(file_data, key)
  file = open(file, "w")
  file.write(file_data)
  file.close()

def config_reader(file, key, group = "", section = ""):
  # group > section > key
  file = file.open(file, "r")
  file_data = file.read()
  file.close()
  
  if group:
    file_data = csf.str_in_bw(file_data, "<{" + group + "}>", "<{/" + group + "}>")
  
  if section:
    file_data = csf.str_in_bw(file_data, "<[" + section + "]>", "<[/" + section + "]>")
  
  value = csf.str_in_bw(file_data, "<" + key + ">", "</" + key + ">")
  return value
    
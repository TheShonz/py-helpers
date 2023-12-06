
# This module contains useful scripts that have broad useability.



# Imports
# -------

import os
import sys
from zipfile import ZipFile
import gzip
import shutil
import re
import pandas as pd
from collections import defaultdict
import pytz
from datetime import date, datetime, timedelta
import time
import secrets
import string
from cryptography.fernet import Fernet



# Functions
# ---------

# Read excel to dataframe and convert to dict to access individual row as dict
# Using defaultdict(list) and 'records' orientation 
# 	to read dict as rows--similar to csv.DictReader
def Excel_to_Dict(path: str, 
					sheet = 0):
	with open(path, mode = 'rb') as source:
		df = pd.read_excel(source, engine = 'openpyxl', sheet_name = sheet).fillna('')

	dd = defaultdict(list)
	excel_dict = df.to_dict(orient = 'records', into = dd)

	return excel_dict


# Convert an Excel file to .csv
def Excel_to_CSV(source: str):
	with open(source, 'rb') as read:
		read_file = pd.read_excel(read, engine = 'openpyxl')
	
	if(os.path.exists(source) and os.path.isfile(source)):
		os.remove(source)

	file  = os.path.basename(source)
	loc = source.rstrip(file)
	source  = loc + file.rstrip('.xlsx') + '.csv'
	read_file.to_csv(source, index = None, header = True)

	del read_file

	return source


# Look for files in a location beginning with a specific string
# returns a list
def Look_for_Files(loc: str, 
					keyword: str = ''):
	list_of_files = []
	for root, dirs, files in os.walk(loc, topdown=False):
		for file in files:
			if file.find(keyword) != -1:
				list_of_files.append(os.path.join(root, file))

	return list_of_files


# Look for dirs in a location beginning with a specific string
# returns a list
def Look_for_Dirs(loc: str, 
					keyword: str = ''):
	list_of_dirs = []
	for root, dirs, files in os.walk(loc, topdown=False):
		for dr in dirs:
			if dr.find(keyword) != -1:
				list_of_dirs.append(os.path.join(root, dr))

	return list_of_dirs


# Looks for the most recent file in a location beginning wiht a specific string
# returns a path
def Find_Most_Recent(loc: str, # 'loc' refers to the dir to look in
						keyword: str = ''): # 'name' is a string to search for at the beginning of the file name
	list_of_files = []

	# Collect a list of files matching the designated names
	list_of_files = Look_for_Files(loc, keyword = keyword)

	# Return the most recently created file
	if list_of_files != []:
		path	= max(list_of_files, key=os.path.getctime)
		return path

	else:
		raise LookupError('Cannot locate file(s) containing keyword: \"' + keyword + '\" in ' + loc)


# Gets the timedelta from the creation of a file to current date
def File_Age(file_path):
	today = datetime.today()

	creation_stamp = datetime.strptime(time.ctime(os.path.getctime(file_path)), "%c")
	today_stamp    = datetime.combine(today, datetime.min.time())
	day_delta 	   = today_stamp - creation_stamp

	return day_delta


# Unzip and relocate the contents of .zip files
def ZipUnZip(source): # 'source' = .zip file path
	source = r'{}'.format(source.strip('"'))
	file   = os.path.basename(source)
	ext    = os.path.splitext(source)[-1].lower()

	# create alternate file names to search for
	name = file.rstrip(ext).replace(' - Copy', '')
	name = re.sub('[(][0-9]*[)]', '', str(name)).strip()

	# establish a new, temporary path for the unpacked file
	new_path = source.rstrip(file) + name + '\\'

	with ZipFile(source, 'r') as zipObj:
		zipObj.extractall(new_path)

	# remove original file
	if os.path.exists(source) and os.path.isfile(source):
		os.remove(source)

	# get a list of the contents of the zip file from the new temp destination
	zip_contents = Look_for_Files(new_path)
	if zip_contents == []:
		raise LookupError('Cannot locate file called ' + file + ' in ' + new_path + '.\nPlease re-run script and input a valid file path.')
	elif len(zip_contents) == 1:
		zip_contents = str(zip_contents[0])

	return zip_contents


# Unzip and relocate the contents of .gz files
def GZUnZip(source): # 'source' = .gz file path

	# establish a new path for when the file is unzipped
	new_file = source.rstrip(os.path.splitext(source)[-1].lower())

	# copy file out of gzip
	with gzip.open(source, 'rb') as file_in:
		with open(new_file, 'wb') as file_out:
			shutil.copyfileobj(file_in, file_out)

	# remove original file
	if os.path.exists(source) and os.path.isfile(source):
		os.remove(source)

	return new_file


# Check for any values equal to 'NaN' or ''
def isEmpty(value): 
	# Check for empty string
	if value == '':
		return value == ''
	# Check for NaN
	elif value != value: 
		return value != value


# Check for Daylight Savings time
def is_dst(timezone = "UTC"):
	# Address blank time zone
	if timezone == '':
		timezone = 'UTC'
	# Import time zone as a time zone object
	tz = pytz.timezone(timezone)
	# Get UTC as local time
	now = pytz.utc.localize(datetime.utcnow())
	# Return bool. If local time now at time zone is in DST
	return now.astimezone(tz).dst() != timedelta(0) # In most cases time delta will be an hour different if in DST


# Generate a string of randomized characters
def Gen_Random_Str(char_len:int, # 'char_len' = int; length of the string to be generated
					sep:str = '', # 'sep' = static character to separate each of the randomized characters
					special:str = '', # 'special' = user-chosen characters to include among possible randomized characters 
					alpha:bool = True, # 'alpha' = bool; to determine whether to include string.ascii_letters among possible randomized characters
					numer:bool = True): # 'numer' = bool; to determine whether to include string.digits among possible randomized characters
	
	if alpha:
		alpha = string.ascii_letters
	else:
		alpha = ''
	if numer:
		numer = string.digits
	else:
		numer = ''

	# Using secrets.choice(), return randomized string of desired length
	return (sep.join(secrets.choice(alpha + numer + special)
		for i in range(char_len)))


# Generate a list of randomized strings
def Gen_Random_List(list_len: int, # 'list_len' = int; number of random strings to generate as list
					str_len: int = 20, # 'str_len' = int; length of each string to be generated
					str_params:dict = None): # 'str_params' = dict; access Gen_Random_Str() args

	params = {'sep': '', 'special': '', 'alpha': True, 'numer': True}
	func_params = ['char_len', 'sep', 'special', 'alpha', 'numer']

	# Determine if all keys passed via str_params are available in Gen_Random_Str()
	if str_params != None and isinstance(str_params, dict):
		if not(all(x in func_params for x in list(str_params.keys()))):
			raise TypeError("Invalid parameter passed.\n{" + 
				", ".join(list(str_params.keys())) + 
				"} contains an invalid parameter.\nPlease select from the following:\n" +
				", ".join(func_params))
		params.update(str_params)

	# Determine if the given list and string length parameters passed
	#   are sufficient to generate the desired list
	abc_len = num_len = spc_len = 0
	if params['alpha']:
		abc_len = len(string.ascii_letters)
	if params['numer']:
		num_len = len(string.digits)
	spc_len = len(params['special'])
	char_poss = (abc_len + num_len + spc_len)**str_len
	if list_len > char_poss:
		raise ValueError('Desired list length exceeds the number of possible variations: ' +
							str(char_poss) + 
							'\nDecrease list length or increase string length (str_len)')
	
	# Generate random strings and append to list
	rndm_lst = []
	while len(rndm_lst) < list_len: 
		rndm_lst.append(Gen_Random_Str(str_len, **params))
		# remove duplicates
		rndm_lst = list(dict.fromkeys(rndm_lst))

	return rndm_lst


# Multiply items within an iterable object
def MultiplyIterable(iterable, # 'iterable' = any object that can be iterated (list, set, str, dict, tuple)
				stop:int = None, # 'stop' = int; the number of iterable objects that should be multiplied
				sort:bool = False, # 'sort' = bool; when True, sort list from smallest to greatest value
				reverse:bool = False): # 'reverse' = bool; when True, reverse list order

	# Convert iterable object to list
	if isinstance(iterable, str):
		iterable = iterable.split()
	if isinstance(iterable, dict):
		items    = list(iterable.items())
		iterable = []
		for x in items:
			iterable.extend(x)
	iterable = list(iterable)

	# establish stopping point for multiplication loop
	if stop == None:
		stop = len(iterable)

	# optional sorted() and reverse() functions
	if sort:
		iterable = sorted(iterable)
	if reverse:
		iterable.reverse()

	# Multiply elements one by one
	count  = 0
	result = 1
	for x in iterable:
		count += 1
		# once loop count exceeds stop, break
		if count > stop:
			break
		# for non-numerical values in list, multiply the length of the value
		if not(isinstance(x, int) or isinstance(x, float)):
			result = result * len(x)
		else:
			result = result * x

	return result


# Find all integers that can be multipled to equal a given number
def Find_Denominators(num):
	denom_list = []
	for n in range(1, num):
		if (num % n) == 0:
			denom_list.append(n)
	denom_list.append(num)

	return denom_list


# Function to remove duplicates from a list
def Remove_Duplicates_List(lst):
	for x in lst:
		for index in range(len(lst)-1):
			if x == lst[index]:
				lst.remove(x)
				break
	
	return lst


# Split a given number into unique pairs of denominators
def Denominator_Pairs(num):
	
	denoms = Find_Denominators(num)

	# generate denominator pair sets
	pair_list = []
	for x in denoms:
		pair = [x, (num//x)]
		pair = sorted(pair)
		pair_list.append(pair)

	# remove duplicate denominator sets
	pair_list = sorted(Remove_Duplicates_List(pair_list))
	
	return pair_list


# Bool check to determine if a number is prime
def Check_Prime(num):
	for i in range(2, num):
		if (num % i) == 0:
			# if factor is found, return False
			return False
		else:
			return True


# Flatten iterables into a single-level list regardless of levels of iterables
def Flat_List(*args, 
			dict_value = None): # 'dict_value' = user-designated value that determines how to handle dict
	out_list = []
	for arg in args:
		# Create list from dictionaries
		if isinstance(arg, dict):
			if (dict_value == 'all' or 
				dict_value == 'items' or
				dict_value == None):
				arg = list(arg.items())
			elif dict_value == 'keys':
				arg = list(arg.keys())
			elif dict_value == 'values':
				arg = list(arg.values())
			else:
				raise KeyError("dict_value must be one of the following: \'all\', \'items\', \'keys\', \'values\', or None ")

		# Flatten iterables into single values
		if not(isinstance(arg, str) or isinstance(arg, dict)) and hasattr(arg, '__iter__'):
			recur_list = []
			for x in arg:
				recur_list.extend(Flat_List(x))
			out_list.extend(recur_list)
		else:
			out_list.append(arg)

	return out_list


# Encrypt a file or string and save to file
def Encrypt_File(obj:(bytes or str), 
				key:'Fernet(Fernet.generate_key())' or str = None, 
				file_path: str = 'FILE.txt', 
				key_path: str = 'KEY.key',
				overwrite: str or bool = True): # 'all', 'obj', 'key', True, False

	# 1. Ensure objects to be encrypted, keys, and output file paths are 
	# 	correctly formatted
	# If the object to be encrypted is a particular file,
	# 	user may pass the file path as the 'obj' argument
	if os.path.exists(obj) and os.path.isfile(obj):
		file_path = obj
		obj 	  = ''
	# If 'obj' is a file, read it in as str
	if (obj == '' and 
		(os.path.exists(file_path) and os.path.isfile(file_path))):
		with open(file_path, 'r') as obj_file:
			obj = obj_file.read()

	# If object is unencoded str, encode
	if not(isinstance(obj, bytes)):
		obj = str(obj).encode('utf-8')
	# If 'obj' is still not bytes object
	if not(isinstance(obj, bytes)):
		raise TypeError("data must be bytes")

	# If the 'key' arg is a file path, open file and use as key
	if (key != None and not(isinstance(key, Fernet)) and 
		(os.path.exists(key) and os.path.isfile(key))):
		key_path = key
		key 	 = ''

	# If the key provided is a file, read it in
	if ((key == '' or key == None) and 
		(os.path.exists(key_path) and os.path.isfile(key_path)) and
		(overwrite and overwrite != 'obj')):
		# read in the key
		try:
			with open(key_path, 'rb') as keyfile:
				read_key = keyfile.read()
			
			# set it as a Fernet object in order to encrypt the credentials
			key = Fernet(read_key)
		except:
			key = Gen_Key(key_path)

	# If 'key' is not yet a Fernet object, generate new key
	if not(isinstance(key, Fernet)):
		if os.path.exists(key_path) and os.path.isfile(key_path):
			# either delete existing file or alter path to avoid identicals
			if not(overwrite) or overwrite == 'obj':
				key_path = Increase_File_Number(key_path)
			else:
				os.system("attrib -h " + key_path)
				os.remove(key_path)

		key = Gen_Key(key_path)

	# 2. Encrypt the object
	enc_obj = key.encrypt(obj)

	# 3. File handling
	# remove original object file
	if os.path.exists(file_path) and os.path.isfile(file_path):
		if not(overwrite) or overwrite == 'key':
			file_path = Increase_File_Number(file_path)
		else:
			os.system("attrib -h " + file_path)
			os.remove(file_path)
			
	# write encrypted, binary cred file
	with open(file_path, 'wb') as encrypted_file:
		encrypted_file.write(enc_obj)


	return file_path, key_path


# Open and decrypt a bytes object or a file encrypted with the Encrypt_File() method
def Decrypt(obj:bytes, 
			key:'Fernet(Fernet.generate_key())'):
	
	if os.path.exists(obj) and os.path.isfile(obj):
		with open(obj, 'r') as obj_file:
			obj = obj_file.read()

	# If object is unencoded str, encode
	if not(isinstance(obj, bytes)):
		obj = str(obj).encode('utf-8')
	# If 'obj' is still not bytes object
	if not(isinstance(obj, bytes)):
		raise TypeError("data must be bytes")

	# read in the key
	if os.path.exists(key) and os.path.isfile(key):
		with open(key, 'rb') as keyfile:
			key = keyfile.read()

		if not(isinstance(key, bytes)):
			key = str(key).encode('utf-8')
		# If 'obj' is still not bytes object
		if not(isinstance(key, bytes)):
			raise TypeError("data must be bytes")

		key = Fernet(key)

	return key.decrypt(obj).decode('utf-8')


# Generate the key using cryptography's Fernet
def Gen_Key(path):
	# generate the key
	key = Fernet.generate_key()

	# write the file
	with open(path, 'wb') as filekey:
		filekey.write(key)

	# set it as a Fernet object in order to encrypt the credentials
	fernet = Fernet(key)

	return fernet


# Alter file names to avoid overwriting
def Increase_File_Number(path):
	# determine if file is numbered
	ext       = os.path.splitext(path)[-1].lower()
	found_num = re.findall('\(\d*\)' + ext, path)
	# if so, increase by 1
	if found_num != []: 
		orig_n   = found_num[-1]
		n        = int(orig_n.strip('()' + ext)) + 1
		format_n = '(' + str(n) + ')' + ext
		path     = path.replace(orig_n, format_n)
	# if not, add "(1)" just before the extension
	else:
		format_n = '(1)' + ext
		path     = path.replace(ext, format_n)

	# if the file path generated is already a file, increase the number
	if os.path.exists(path) and os.path.isfile(path):
		path = Increase_File_Number(path)

	return path


# Find the next date of a given weekday
def Date_by_Weekday(day: str or int, weeks_out: int = 0):
	# convert string day to weeknumber
	if isinstance(day, str):
		week_dict = {
			'monday': 0, 
			'tuesday': 1, 
			'wednesday': 2, 
			'thursday': 3, 
			'friday': 4, 
			'saturday': 5, 
			'sunday': 6}
		day = week_dict[day.strip().lower()]

	# calculate days until the desired day
	days_until = timedelta(days = day - (date.today().weekday()))

	# determine the days until by subtracting today's weeknumber from the desired date's
	if days_until.days < 0:
		days_until += timedelta(days = 7)
	
	# apply weeks out modifier
	days_until += timedelta(weeks = weeks_out)

	return date.today() + days_until


# Determine if an object has a specified method and if that method is callable
def has_method(obj, method: str):
	mthd = getattr(obj, method, False)
	return mthd, callable(mthd)

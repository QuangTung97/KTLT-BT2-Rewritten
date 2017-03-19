import MySQLdb
import sys
import datetime

# connect to database
try:
	db = MySQLdb.connect(host="localhost", user="ktlt", passwd="taquangtung", db="MONITOR", cursorclass=MySQLdb.cursors.SSCursor)
except Exception, e:
	print "Can't connect to database"

def bytesToMegabytes(n):
	return n / 1024 / 1024

def existingUser(userID):
	cursor = db.cursor()
	try:
		userExists = cursor.execute("SELECT USER_NAME FROM PREDICTION WHERE UID = %s", userID)
	except Exception, e:
		print "existingUser"
		print repr(e)
	cursor.close()

	if userExists == 0

# Find last server and log in time to decide if RAM cache is importtant 
def lastUsedServer(userID):
	cursor = db.cursor()
	try:
		lastServer, lastLogin = cursor.execute("SELECT LAST_USED_SERVER, LAST_LOGIN FROM PREDICTION WHERE UID = %s", userID)
	except Exception, e:
		print "lastUsedServer"
		print repr(e)
	cursor.close()

	return lastServer, lastLogin

# Find the RAM load on the server since last login


def predictUserLoad(userID):
	# A test to see if the user already exits in the Prediction table
	sqlSelectUser = ("SELECT UID FROM PREDICTION WHERE UID = %s", (userID, ))
	userExists = cursor.execute(sqlSelectUser)
	
	# Get the monitored data for the user from the user monitor table
	sqlSelect = ("SELECT MAX(CPU), MAX(RAM), AVG(CPU), AVG(RAM), MAX(RUN_TIME) FROM jSAMPLE WHERE UID = %s", (userID, ))
	maxCPU, maxRAM, avgCPU, avgRAM, runTime = cursor.execute(sqlSelect)

	# Get the user name and which server the user was last logged in to
	sqlSelect =  ("SELECT NAME, SERVER FROM USER WHERE UID = %s", (userID, ))
	name, server = cursor.execute(sqlSelect)

	# if the user doesn't exist we insert the new user which the data from the user monitor table
	if userExists == 0:
		print "if userExists"
		sqlInsert = ("INSERT INTO PREDICTION (UID, USER_NAME, LAST_USED_SERVER, LAST_LOGIN, AVG_CPU, MAX_CPU, AVG_RAM, MAX_RAM) VALUES = (%s, %s, %s, %s, %s, %s, %s, %s)", (userID, name, server, runTime, avgCPU, maxCPU, avgRAM, maxRAM))
		cursor.execute(sqlInsert)
	# if the user already exists in the precdiction table we combine the exist data with the new monitored data
	else:
		sqlSelect = ("SELECT AVG_CPU, MAX_CPU, AVG_RAM, MAX_RAM FROM PREDICITON WHERE UID = %s", (userID, ))
		preAvgCPU, preMaxCPU, preAvgRAM, preMaxRAM = cursor.execute(sqlSelect)

		# We want to adjust the value of average CPU for the user in the prediction table by using an algorithm tha can adjust the value based on the difference
		difference = avgCPU - preAvgCPU
		newAvgCPU = changeAlgorithm(avgCPU, preAvgCPU, difference)

		# We want to adjust the value of average RAM for the user in the prediction table by using an algorithm that can adjust the value based on the difference
		difference = avgRAM - preAvgRAM
		newAvgRAM = changeAlgorithm(avgRAM, preAvgRAM, difference)

		# We check if the user have heavier CPU jobs running in the system
		if maxCPU > preMaxCPU:
			newMaxCPU = maxCPU
		else:
			newMaxCPU = preMaxCPU

		# Check if the user have heavier RAM jobs running in the system
		if maxRAM > preMaxRAM:
			newMaxRAM = maxRAM
		else:
			newMaxRAM = preMaxRAM
		# Update the prediction table with the new calculated data
		sqlInsert = ("UPDATE PREDICTION SET LAST_USED_SERVER = %s, LAST_LOGIN = %s, AVG_CPU = %s, MAX_CPU = %s, AVG_RAM = %s, MAX_RAM = %s WHERE UID = %s", (server, runTime, newAvgCPU, newMaxCPU, newAvgRAM, newMaxRAM, userID))
		cursor.execute(sqlInsert)

		# Clean up the user monitor table
		sqlDelete = ("DELETE FROM jSAMPLE WHERE UID = %s AND RUN_TIME < %s", (userID, runTime))
		cursor.execute(sqlDelete)


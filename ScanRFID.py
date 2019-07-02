#! /usr/bin/python
# coding: utf8
'''
__author__  = "David Pfeifle"
__version__ = "0.0.72"
'''

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, timedelta
import RPi.GPIO as g
import MFRC522
import signal
import time
import os

read = True
id_nr_none = 9999
room = 'r1'
user_id = ''
meeting_id = ''
sleep_time = 1


# exit prog
def exit_Prog(signal, frame):
	global read
	read = False
	g.cleanup()
	print('The program was terminated.')
	
	
# check if room is free
def get_room():
	try:
		doc = db.collection(u'rooms').document(u''+room).get()
		return bool(u'{}'.format(doc.to_dict()[u'frei']) == 'True')
		
	except:
		return None


# get document-id by tag-id
def get_user(user):
	global user_id
	user_id = None
	try:
		docs = db.collection(u'user').where(u'uidRFID', u'==', u''+str(user)).get()
		for doc in docs:
			user_id = doc.id
			
		print('user Id:', user_id)
		return True if user_id else False
		
	except:
		print('User not found')
		return False


# get if User has a Meeting
def get_meeting():
	global meeting_id
	meeting_id = None
	try:
		docs = db.collection(u'meetings').where(u'hostID', u'==', u''+user_id).where(u'room', u'==', u''+room).get()
		for doc in docs:
			meeting_id = doc.id
			print('meeting id:', meeting_id)
			
			# get start and end time from firebase and time now
			if meeting_id:
				time_start = datetime.strptime(doc.to_dict()[u'dateAndTimeStart'][:23], '%Y-%m-%dT%H:%M:%S.%f')
				time_end = datetime.strptime(doc.to_dict()[u'dateAndTimeEnd'][:23], '%Y-%m-%dT%H:%M:%S.%f')
				time_now = datetime.now() + timedelta(hours=1)
				
				# if time now is between start and end
				if time_now <= time_end and time_now >= time_start:
					return True
		
		# if user has no meeting in that period
		return False
		
	except:
		return None


# set 'free' true or false
def set_room():
	buffer = get_room()
	try:
		doc = db.collection(u'rooms').document(u''+room)
		
		# if room is joyful
		if buffer:
			doc.update({u'frei': False})
			print(room+': frei is now false')
		
		# if room not found 
		elif buffer == None:
			print('Room not Found')

		# if room is occupied
		else:
			doc.update({u'frei': True})
			print(room+': frei is now true')
	
	except:
		print('Firebase Error: set_room()')



# main method
if __name__ == '__main__':
	# init Firebase
	cred = credentials.Certificate('/home/pi/smartOffice/adm.json')
	firebase_admin.initialize_app(cred)
	db = firestore.client()	

	# init rfid reader
	id_nr = id_nr_none
	signal.signal(signal.SIGINT, exit_Prog)
	mifare = MFRC522.MFRC522()
	
	# init leds
	g.setmode(g.BOARD)
	g.setup(11, g.OUT) # running LED - blue
	g.setup(13, g.OUT) # auth Ok	 - green
	g.setup(15, g.OUT) # auth Failed - red
	g.output(11,1)
	
	# print on console
	print('The program was started.')
	print('Press Ctrl+C to exit.')

	# run reading
	while read:
		(status,uid) = mifare.MFRC522_Request(mifare.PICC_REQIDL)
		
		# if card founded
		if status == mifare.MI_OK:
			logged = False
			try:
				# get UID
				(status,uid) = mifare.MFRC522_Anticoll()
				id_nr = ''.join(map(str, uid))
				print('Card UID:', str(uid[0]),str(uid[1]),str(uid[2]),str(uid[3]),str(uid[4]))
				print('Id Number', id_nr)
			
			except:
				id_nr = id_nr_none
				print('Failed to read card.')
			
			# if can read dard could be read
			if id_nr != id_nr_none:
				g.output(11,0)
				
				# get user id from firebase
				if get_user(id_nr):
					buffer = get_meeting()
					
					# if user has meeting
					if buffer:
						set_room()
						logged = True
						
					# if no meeting found
					elif buffer == None:
						print('No Meeting found')
						
					# if meeting isnt now
					else:
						print('You dont have a meeting now')
				
				# user not found in firebase
				else:
					print('user does not exist')
						
				# show green light 
				if logged:
					g.output(13,1)
					time.sleep(sleep_time) 
					g.output(13,0)
					
				# show red light
				else: 
					g.output(15,1)
					time.sleep(sleep_time)
					g.output(15,0)
					
				# show blue light
				g.output(11,1)
				logged = False
				print('')
				
		else:
			id_nr = id_nr_none

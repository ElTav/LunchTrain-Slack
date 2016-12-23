import threading
import time
import requests
import json

class Train(object):
	def __init__(self, conductor, destination, departureTime):
		self.TimeRemaining = departureTime
		self.DisplayDestination = destination
		self.MapDestination = destination.lower()
		self.Passengers = set([conductor])
		self.Lock = threading.Lock()
	
	def AddPassenger(self, passenger):
		self.Lock.acquire()
		if passenger in self.Passengers:
			self.Lock.release()
			return "%s is already on the train to %s" % (passenger, self.DisplayDestination)
		self.Passengers.add(passenger)
		self.Lock.release()
		return None
	
	def PassengerString(self):
		self.Lock.acquire()
		res = ""
		numPassengers = len(self.Passengers)
		i = 0
		for passenger in self.Passengers:
			res += passenger
			if i != numPassengers - 1:
				res += ", "
			if i == numPassengers - 2:
				res += "and "
			i += 1
		self.Lock.release()
		return res

class Station(object):
	def __init__(self):
		self.Lock = threading.Lock()
		self.Trains = {}
	
	def AddTrain(self, train):
		if train.MapDestination in self.Trains:
			return "There's already a train to %s" % train.MapDestination
		else:
			self.Trains[train.MapDestination] = train
			return None
	
	def DeleteTrain(self, destination):
		res = self.Trains.pop(destination, None)
		if res is None:
			return res
		return "The train to %s doesn't exist so it can't be removed" % destination
	
	def ActiveTrainCommand(self):
		self.Lock.acquire()
		res = "There are trains to: "
		i = 0
		numTrains = len(self.Trains)
		if numTrains == 0:
			self.Lock.release()
			return "There are currently no active trains"
		for dest in self.Trains:
			train = self.Trains[dest]
			if numTrains == 1:
				self.Lock.release()
				return "There is currently a train to %s in %d mins (with %s on it)" % (train.DisplayDestination, train.TimeRemaining, train.PassengerString())
			else:
				res += "%s in %d mins (with %s on it)" % (train.DisplayDestination, train.TimeRemaining, train.PassengerString())
			if i != numTrains - 1:
				res += ", "
			if i == numTrains - 2:
				res += "and "
			i += 1 
		self.Lock.release()
		return res
	
	def HelpCommand(self):
		return "Usage: /train start <destination> <minutes> || /train join <destination> || /train active"
	
	def JoinTrainCommand(self, passenger, destination):
		self.Lock.acquire()
		destination = destination.lower()
		res = ""
		if destination in self.Trains:
			oldTrain = self.GetPassengerTrain(passenger)
			if oldTrain is not None and oldTrain.MapDestination != destination:
				res = self.DitchTrain(passenger, destination)
			train = self.Trains[destination]
			err = train.AddPassenger(passenger)
			self.Lock.release()
			if err is not None:
				return err
			elif res == "":
				res = "%s jumped on the train to %s" % (passenger, train.DisplayDestination)	
				return res	
			else:
				return res
		else:
			self.Lock.release()
			return "That train doesn't exist, please try again or find a new train to join"
	
	def DitchTrain(self, passenger, destination):
		oldTrain = self.GetPassengerTrain(passenger)
		res = "%s ditched their train to %s in favor of one to %s." % (passenger, oldTrain.DisplayDestination, destination)
		oldTrain.Lock.acquire()
		oldTrain.Passengers.remove(passenger)
		oldTrain.Lock.release()
		if len(oldTrain.Passengers) == 0:
			self.DeleteTrain(oldTrain.MapDestination)
		return res

	def GetPassengerTrain(self, passenger):
		for dest in self.Trains:
			train = self.Trains[dest]
			if passenger in train.Passengers:
				return train
		return None
	def StartTrainCommand(self, conductor, destination, time):
		self.Lock.acquire()
		res = ""
		oldTrain = self.GetPassengerTrain(conductor)
		if oldTrain is not None and oldTrain.MapDestination != destination:
			res = self.DitchTrain(conductor, destination)
		newTrain = Train(conductor, destination, time)
		err = self.AddTrain(newTrain)
		if err is not None:
			self.Lock.release()
			return err
		else:
			if res != "":
				res += "\n"
			res += "%s has started a train to %s that leaves in %d minutes!" % (conductor, newTrain.DisplayDestination, newTrain.TimeRemaining)
			if newTrain.TimeRemaining == 1:
				res = "%s has started a train to %s that leaves in %d minute!" % (conductor, newTrain.DisplayDestination, newTrain.TimeRemaining)
		self.Lock.release()
		worker = TrainWorker(self, newTrain)
		worker.start()
		return res


def GetTime(message):
	if IsInt(message[-1]):
		time = int(message[-1])
		if time <= 0:
			return None, "Please specify a time greater than 0 mins"
		return int(message[-1]), None
	else:
		return None, "Couldn't parse your time to departure. Please make sure it's an int >= 1"

def IsInt(val):
	try:
		int(val)
		return True
	except:
		return False


class TrainWorker(threading.Thread):
	def __init__(self, station, train):
		threading.Thread.__init__(self)
		self.Station = station
		self.Train = train
		# Implement a separate counter (in seconds) to refresh the station more "instantaneously"
		self.TimeRemaining = train.TimeRemaining * 60
	def run(self):
		while self.TimeRemaining >= 0:
			time.sleep(1)
			self.TimeRemaining -= 1
			if len(self.Train.Passengers) == 0 or self.Train.MapDestination not in self.Station.Trains:
				return
			message = ""
			if self.TimeRemaining == 60:
				message = "Reminder, the next train to %s leaves in one minute" % self.Train.DisplayDestination
			elif self.TimeRemaining == 0:
				message = "The train to %s has left the station with %s on it!" % (self.Train.DisplayDestination, self.Train.PassengerString())
				self.Station.DeleteTrain(self.Train.MapDestination)
			if message != "":
				PostMessage(message)

def Handler(station, user, message):
	message = message.split(' ')
	command = message[0]
	message = message[1:]
	notFound = "Your train/destination could not be found, please try again"
	if command == "help":
		return station.HelpCommand()
	elif command == "active" and len(message) == 0:
		return station.ActiveTrainCommand()
	elif command == "join" and len(message) >= 1:
		if len(message) == 0:
			return notFound
		else:
			return station.JoinTrainCommand(user, ' '.join(message))
	elif command == "start" and len(message) >= 2:
		time, err = GetTime(message)
		destination = message[:-1]
		destination = ' '.join(destination)
		if err is not None:
			return err
		elif len(destination) == 0:
			return notFound
		else:
			return station.StartTrainCommand(user, destination, time)
	else:
		return "Your command could not be found or was malformed, please view the help message (/train help) for more details"


def PostMessage(message):
	webhook_url = 
	slack_data = {'text': message, 'response_type': 'in_channel'}
	response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

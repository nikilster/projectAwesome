'''
	Data Object

	Base class which knows how to serialize to json
	and create from json
'''
import json
import inspect

class Data:
	
	#Save all of the attributes to JSON
	#Only Instance variables (not class variables)
	def toJson(self):
		return json.dumps(self.__dict__)

	#Load the object from json
	def setFromJson(self, jsonData, fields):
	
		#Get
		dict = json.loads(jsonData)
		
		#Save
		#TODO: make these mandatory
		for field in fields:
			self.__setAttr(field, dict)

	#Returns the dictionary representation of the object so that it can be jsonified in an an array
	#(for Picture) Also turn any embedded objects into dictionaries
	def toDictionary(self):
		dict = self.__dict__

		#if we have any object
		# (which are subclasses of Data)
		for key in dict.keys():
			value = dict[key]

			#Dictionary it
			if(isinstance(value, Data)):
				dict[key] = value.toDictionary()

		return dict

	#Private (Not Really Private) Helper Methods
	#http://stackoverflow.com/questions/70528/why-are-pythons-private-methods-not-actually-private
	def __setAttr(self, key, dict):
		if(key in dict):
			self.__dict__[key] = dict[key]
		else:
			self.__dict__[key] = ""

	#Python "To String"
	#We are just going to print all of the fields of the object
	#In a pretty
	def __repr__(self):

		objectRepresentation = "<" + self.__class__.__name__
		for key in self.__dict__.keys():
			attribute = " " + key + ":" + str(self.__dict__[key]) + " "
			objectRepresentation += attribute 

		objectRepresentation += ">"

		return objectRepresentation
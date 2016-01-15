#!/usr/bin/env python

import sys
import os
from androguard.core.bytecodes import apk
from androguard.util import read
import xml.dom.minidom
import glob
import re
from pyspark import SparkConf, SparkContext
from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.linalg import Vectors
from string import whitespace

conf = SparkConf().setMaster("local[4]").setAppName("reduce")
conf.set("spark.executor.memory", "4g")
sc = SparkContext(conf=conf)

#Create folders for storing the xml files
print "File creation"
goodxmlpath="xml/good/"
if not os.path.exists(os.path.dirname(goodxmlpath)):
	print "directory added"	
	os.makedirs(os.path.dirname(goodxmlpath))

badxmlpath="xml/bad/"
if not os.path.exists(os.path.dirname(badxmlpath)):
	print "directory added"		
	os.makedirs(os.path.dirname(badxmlpath))


featurevectorcsv="output/feature_vectors.csv"
featuredb="dependencies/Feature_List.txt"

if os.path.isfile(featurevectorcsv):
	os.remove(featurevectorcsv)
feature_vectors = open(featurevectorcsv, "a")

#Write the header for the csv file from the Feature_List.txt file  
list = open(featuredb, "r").read().splitlines()
a = 0
attribute = ["APP_NAME"]
while a < len(list):
	attribute.append(", " + list[a])
	a+=1
attribute.append(", " + "isMalware")
attributes = ''.join(attribute)
feature_vectors.write(attributes)


#This function extracts manifest.xml files using Androguard from the apk files
def getmanifest(filepath,isMalware):
	for file in glob.glob(filepath):
		
		shortNameExt = os.path.basename(file)
		#print shortNameExt
		shortName = os.path.splitext(shortNameExt)[0]
		shortName = shortName+".xml"
		shortname = shortName.replace(" ","")

		
		apkFile = file
		try:	
			a = apk.APK(apkFile)
			manifest = a.get_android_manifest_xml()
			if hasattr(manifest,'toprettyxml'):
				xml=manifest.toprettyxml()
				print ("Successfully extracted features from "+shortName)
			else:
				continue
			
		except:
			print("Unable to read application " + shortname)
				
			
		
		if isMalware:
			completeName = os.path.join(badxmlpath, shortName)   
		else:
			completeName = os.path.join(goodxmlpath, shortName)

		f =  open(completeName, "wb")
		xml=xml.encode('ascii','ignore')
		f.write(xml)
		f.close()

#This function extracts permissions from the manifest.xml file and returns the application name and list of permissions
def flat_map(document):
        
       
	words = re.findall(r'(?:<uses-permission.*android.*permission.)(.*)(?:">)',document[1]) # get the list of all the words
	parts = document[0].split(":")
	filename=os.path.basename(parts[1])
	filename=filename.replace(" ","")
	#filename=filename.translate(None, whitespace)
	#head,tail=parts[1].split("/")
	appname=filename.strip('.xml')
	#print name
	exist = [];
	for word in words:
		#print word
		if word not in exist:
			exist.append(word)
	#print "new doc"
	if not exist:
		exist.append("empty")
		
	
	return filename,exist

#This function writes the permissions in a CSV file  
def writetoCSV(appname,features,mal):
	
	i=0
	rep = False
	while i < len(features):
		j = i+1
		while j < len(features):
			if features[i] == features[j]:
				del features[j]
				rep = True
			j = j+1
		i = i+1
	
	if rep == True:
		features.append(":repetition:")
	
	list = open(featuredb, "r").read().splitlines()
	vector = ["\n" + appname]
	m=0
	while m < len(list):
			exists = False
			n = 0
			while n < len(features):
				if(list[m] == features[n]):
					exists = True
					vector.append(", 1")
					
					break
				n+=1
			if exists == False:
				vector.append(", 0")
				
			m+=1
	##isMALWARE
	if mal:
			vector.append(", 1")
			
	else:
			vector.append(", 0")
			
	vectors = ''.join(vector)
	feature_vectors.write(vectors)		






print "Extracting feature vector from malware samples"
getmanifest("app_files/apk/bad/*.apk",True)
pages = sc.wholeTextFiles(badxmlpath+"*")
features=pages.map(flat_map).collect()
for item in features:
	print item[0]
	print item[1]
	if 'empty' in item[1]:	
		print("Do not write to CSV since feature set is empty")
	else: 
		writetoCSV(item[0],item[1],True)

print"========================================================================"
print "Extracting feature vector from benign samples"
getmanifest("app_files/apk/good/*.apk",False)
pages = sc.wholeTextFiles(goodxmlpath+"*")
features=pages.map(flat_map).collect()
for item in features:
	print item[0]
	print item[1]
	if 'empty' in item[1]:	
		print("Do not write to CSV since feature set is empty")
	else:
		writetoCSV(item[0],item[1],False)



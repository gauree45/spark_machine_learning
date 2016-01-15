from pyspark.mllib.classification import NaiveBayes
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.linalg import Vectors
from pyspark import SparkConf, SparkContext

#This function extracts the label and features 
#The label is "isMalware" 
def parseLine(line):
	parts=line.split(',')
	label=int(parts[152])
	features=Vectors.dense([int(x) for x in parts[1:151]])
	#print parts[152]
	return LabeledPoint(label,features)


conf = SparkConf().setMaster("local[4]").setAppName("reduce")
conf.set("spark.executor.memory", "4g")
sc = SparkContext(conf=conf)
data=sc.textFile("output/feature_vectors.csv")
header=data.take(1)[0]

#Filter out the header from the csv file
rows=data.filter(lambda line : line!=header)
parsedData=rows.map(parseLine)

#Divide data into training and test data
training,test=parsedData.randomSplit([0.8, 0.2], seed = 0)


#train the model
model=NaiveBayes.train(training,1.0)
labelsAndPreds=test.map(lambda p:(model.predict(p.features),p.label))

#calculate the accuracy of naive bayes
accuracy=1.0*labelsAndPreds.filter(lambda(x,v):x==v).count()/test.count()


print("Accuracy of naive bayes is  %f" % (accuracy))

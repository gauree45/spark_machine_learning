# spark_machine_learning
Contents of spark_project.zip

2.output:This folder will store the output of extract.py
3.dependencies: This folder contains feature_List.txt file
4.androguard : This is an open source tool used by the program to extract apk files
5.xml: This folder contains already extracted xml files which will be replaced on running extract.py


Directions for Execution:
1.Extract the spark_project.zip folder
2.Extract the folder app_files.zip shared on Dropbox inside spark_project folder
3.Run the program extract.py using the command "spark-submit extract.py"
	This program will generate a folder xml which will contain the extracted xml files
	This program will also generate a feature_vector.csv file in output folder.
4.Run the program naive.py using the command "spark-submit naive.py"

import os

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__,"../../datafile"))
FILE_NAME = FILE_DIRECTORY + f"/dc_inside_test.csv"

f = open(FILE_NAME,'a')
for i in range(1,11):
	data = "%d\n" % i
	f.write(data)
f.close()


#!usr/bin/python

"""Class for processing the sensor data obtained from the
eu.luanca.HRV app (HappyHeart).
You will have to change the paths so it works for you.
"""
import matplotlib.pyplot as plt


class Processdata:

    """Returns a graph of a file of data"""

    def __init__(self):
        """ ATM just includes the description and authors."""
        self.description = "returns a graph"
        self.author = "Andre Castro Lundin"
        """Variables unique to each instance"""

        self.serial = []  # Current time in milliseconds (java from 1970). Increases linearly
        self.stx = []  # constant
        self.msgId = []  # Constant.Message Id
        self.dlc = []  # constant
        self.firmwareId = []  # constant
        self.firmwareVersion = []  # constant
        self.hardWareId = []  # Constant
        self.hardwareVersion = []  # Constant
        self.batteryIndicator = []  # Battery. Very unreliable
        self.heartRate = []  # Heart rate in BPM
        self.heartBeatNumber = []  # int of assigned number of latest heartbeat. Int 2^8
        # Heart beat timestamps. Last 15. Int 2^16
        self.hbTime1 = []
        self.hbTime2 = []
        self.hbTime3 = []
        self.hbTime4 = []
        self.hbTime5 = []
        self.hbTime6 = []
        self.hbTime7 = []
        self.hbTime8 = []
        self.hbTime9 = []
        self.hbTime10 = []
        self.hbTime11 = []
        self.hbTime12 = []
        self.hbTime13 = []
        self.hbTime14 = []
        self.hbTime15 = []
        # Unused
        self.reserved1 = []
        self.reserved2 = []
        self.reserved3 = []
        self.distance = []
        self.speed = []
        self.strides   = []
        self.reserved4 = []
        self.reserved5 = []
        self.crc = []
        self.etx = []  # constant
        # position coordinates
        self.lat = []
        self.lon = []

    def open_file(self, foldername):
        """Load file called HRV from folder
        """
        with open("D:\\Dropbox\\Advanced project\\" + foldername + "\\HRV.txt") as f:
            for line in f:
                line = line.split(',')
                self.serial.append(line[0])
                self.stx.append(line[1])
                self.msgId.append(line[2])
                self.dlc.append(line[3])
                self.firmwareId.append(line[4])
                self.firmwareVersion.append(line[5])
                self.hardWareId.append(line[6])
                self.hardwareVersion.append(line[7])
                self.batteryIndicator.append(line[8])
                self.heartRate.append(line[9])
                self.heartBeatNumber.append(line[10])
                self.hbTime1.append(line[11])
                self.hbTime2.append(line[12])
                self.hbTime3.append(line[13])
                self.hbTime4.append(line[14])
                self.hbTime5.append(line[15])
                self.hbTime6.append(line[16])
                self.hbTime7.append(line[17])
                self.hbTime8.append(line[18])
                self.hbTime9.append(line[19])
                self.hbTime10.append(line[20])
                self.hbTime11.append(line[21])
                self.hbTime12.append(line[22])
                self.hbTime13.append(line[23])
                self.hbTime14.append(line[24])
                self.hbTime15.append(line[25])
                self.reserved1.append(line[26])
                self.reserved2.append(line[27])
                self.reserved3.append(line[28])
                self.distance.append(line[29])
                self.speed.append(line[30])
                self.strides.append(line[31])
                self.reserved4.append(line[32])
                self.reserved5.append(line[33])
                self.crc.append(line[34])
                self.etx.append(line[35])

                #in case first data set without location
                try:
                    self.lat.append(line[36])
                    self.lon.append(line[37])
                except ValueError:
                    print "no location in file"

        print "File Loaded"

    def generate_graph(self, foldername, x = None, y= None):
        """Load file called HRV from folder
        Returns a graph.
        Default x: timepstamp
        Default y: Heartrate
        """
        self.open_file(foldername)

        if x is None:
            x = self.serial
        if y is None:
            y = self.heartRate

        #for time, set first to self.serial
        plt.plot(x,  y, 'r')
        plt.show()

    def generategHRVfile(self,foldername):
        """Load file called HRV from folder and output
        gHRV friendly file
        """
        self.open_file(foldername)

        """The instantaneous heart rate can be defined as the inverse
        of the time separation between two consecutive heart beats.
        Once the beats have been loaded, the heart rate is calculated.
        In mathematical terms, this corresponds to the calculation of
        the series:
        HR(i)=1000/[T(i)-T(i-1)]
        where HR(i) is the instantaneous heart rate, and T(i) is the
        position of the i-th beat, measured in milliseconds."""

        #WARNING: There are two options: Only taking the heart beats
        # where both are registered or when there is a gap of two,
        # cut them in half. I'm going with the first option

        #First timestamp
        timezero = float(self.hbTime2[0])
        beatprevious = float(self.heartBeatNumber[0])-1

        #For file
        finallist = []

        #Counter the resets for hbnumber and hbtime
        reset1 = 0
        toadd1 = 65536
        reset2 = 0
        toadd2 = 256

        #Iterate while fixing ISSUE WITH 2^16 reset of timestamp and 2^8 heartbeat number reset.
        #can be expanded up to 13 skipped beats, currently 5
        for i in range(len(self.serial)):
            #if two heartbeats in a row
            if (float(self.heartBeatNumber[i])+reset2 == beatprevious + 1) \
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i]) == 0 ) :

                #Check if hbtimestamp resets
                if float(self.hbTime1[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if(beatprevious-reset2 == 255) and float(self.heartBeatNumber[i]) == 0:
                    reset2+=toadd2


            #if it skips a beat
            elif (float(self.heartBeatNumber[i])+reset2 == beatprevious + 2) \
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==1 ):

                #Check if hbtimestamp resets
                if float(self.hbTime2[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime2[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime2[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime1[i])+reset1 > float(self.hbTime2[i])+reset1:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==1 ):
                    reset2+=toadd2

            #if it skips 2 beats
            elif float(self.heartBeatNumber[i])+reset2 == beatprevious + 3\
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==2 ):

                #Check if hbtimestamp resets
                if float(self.hbTime3[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime3[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime3[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime2[i])+reset1 > float(self.hbTime3[i])+reset1:
                    tempvalue = ((float(self.hbTime2[i])+reset1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime2[i])+reset1+toadd1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime1[i])+reset1 > float(self.hbTime2[i])+reset1:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious == 254) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==2 ):
                    reset2+=toadd2

            #if it skips 3 beats
            elif float(self.heartBeatNumber[i])+reset2 == beatprevious + 4\
                    or ((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==3 ):

                #Check if hbtimestamp resets
                if float(self.hbTime4[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime4[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime4[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime3[i])+reset1 > float(self.hbTime4[i])+reset1:
                    tempvalue = ((float(self.hbTime3[i])+reset1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime3[i])+reset1+toadd1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime2[i])+reset1 > float(self.hbTime3[i])+reset1:
                    tempvalue = ((float(self.hbTime2[i])+reset1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime2[i])+reset1+toadd1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime1[i])+reset1 > float(self.hbTime2[i])+reset1:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==3 ):
                    reset2+=toadd2

            #if it skips 4 beats
            elif float(self.heartBeatNumber[i])+reset2 == beatprevious + 5\
                    or ((beatprevious-reset2 == 251) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==3 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==4 ):

                #Check if hbtimestamp resets
                if float(self.hbTime5[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime5[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime5[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime4[i])+reset1 > float(self.hbTime5[i])+reset1:
                    tempvalue = ((float(self.hbTime4[i])+reset1)-(float(self.hbTime5[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime4[i])+reset1+toadd1)-(float(self.hbTime5[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime3[i])+reset1 > float(self.hbTime4[i])+reset1:
                    tempvalue = ((float(self.hbTime3[i])+reset1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime3[i])+reset1+toadd1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime2[i])+reset1 > float(self.hbTime3[i])+reset1:
                    tempvalue = ((float(self.hbTime2[i])+reset1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime2[i])+reset1+toadd1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime1[i])+reset1 > float(self.hbTime2[i])+reset1:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if((beatprevious-reset2 == 251) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==3 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==4 ):
                    reset2+=toadd2

            #if it skips 5 beats
            elif float(self.heartBeatNumber[i])+reset2 == beatprevious + 5\
                    or ((beatprevious-reset2 == 250) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 251) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==3 )\
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==4 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==5 ):

                #Check if hbtimestamp resets
                if float(self.hbTime6[i])+reset1 > timezero:
                    tempvalue = ((float(self.hbTime6[i])+reset1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime6[i])+reset1+toadd1)-timezero)/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime5[i])+reset1 > float(self.hbTime6[i])+reset1:
                    tempvalue = ((float(self.hbTime5[i])+reset1)-(float(self.hbTime6[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime4[i])+reset1+toadd1)-(float(self.hbTime5[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime4[i])+reset1 > float(self.hbTime5[i])+reset1:
                    tempvalue = ((float(self.hbTime4[i])+reset1)-(float(self.hbTime5[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime4[i])+reset1+toadd1)-(float(self.hbTime5[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime3[i])+reset1 > float(self.hbTime4[i])+reset1:
                    tempvalue = ((float(self.hbTime3[i])+reset1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime3[i])+reset1+toadd1)-(float(self.hbTime4[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime2[i])+reset1 > float(self.hbTime3[i])+reset1:
                    tempvalue = ((float(self.hbTime2[i])+reset1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime2[i])+reset1+toadd1)-(float(self.hbTime3[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                if float(self.hbTime1[i])+reset1 > float(self.hbTime2[i])+reset1:
                    tempvalue = ((float(self.hbTime1[i])+reset1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                else:
                    tempvalue = ((float(self.hbTime1[i])+reset1+toadd1)-(float(self.hbTime2[i])+reset1))/1000
                    finallist.append(tempvalue)#save as seconds
                    reset1+=toadd1

                #If the hbnumber resets
                if((beatprevious-reset2 == 250) and float(self.heartBeatNumber[i]) ==0 ) \
                    or ((beatprevious-reset2 == 251) and float(self.heartBeatNumber[i])==1 ) \
                    or ((beatprevious-reset2 == 252) and float(self.heartBeatNumber[i])==2 )\
                    or ((beatprevious-reset2 == 253) and float(self.heartBeatNumber[i])==3 )\
                    or ((beatprevious-reset2 == 254) and float(self.heartBeatNumber[i])==4 )\
                    or ((beatprevious-reset2 == 255) and float(self.heartBeatNumber[i])==5 ):
                    reset2+=toadd2

        #TODO: ADD UP TO 13(?) SKIPPED BEATS (maximum we have encountered, though it logs up to 15 measurements per package)
            else:
                if int(self.heartBeatNumber[i]) == int(beatprevious-reset2):
                    print "RECEIVED REPEATED PACKAGE " + self.heartBeatNumber[i]+ " at time " + self.serial[i]
                else:
                    print "SKIPPED MORE THAN 5 BEATS " + self.heartBeatNumber[i] + " to " + str(beatprevious-reset2) + "timestamp: " + self.serial[i]

            #Debugging: Catch errors
            if tempvalue > 2 or tempvalue < 0.3:
                    print "value: " + str(tempvalue) + " timestamp: " + str(self.serial[i])

            #no matter what, it becomes previous beat
            timezero = float(self.hbTime1[i])+reset1
            beatprevious = float(self.heartBeatNumber[i])+reset2

        #save to file
        with open('D:\\Dropbox\\Advanced project\\Export' + foldername+ '.txt', 'w') as thefile:
            for item in finallist:
                thefile.write("%s\n" % item)

#How to run it:
x = Processdata()

#Generate a graph
#x.generate_graph("data2015-10-21andre")

#Output gHRV friendly file
x.generategHRVfile("data2015-10-21mikkel")

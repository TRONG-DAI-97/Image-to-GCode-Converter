#karpeDiem 29/05/2017
#(c) Beeclust - Multi-Robot Systems Labs, SRM University

from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import cv2
import termcolor
import ast
import copy
import argparse


class ImageToGcode():
    def __init__(self,
                 img,
                 verbose=False):
        self.img = cv2.imread(img,0)
        self.output = ""
        self.outFile = os.path.splitext(os.path.abspath(img))[0]+".gco"
        self.spread = 3.175
        self.nozzles = 12
        self.increment = self.spread/self.nozzles
        self.printArea = [200, 200]
        self.feedrate = 1000
        self.black = 255
        self.offsets = [0, 0]
        self.debug_to_terminal()
        self.make_gcode()

    def make_gcode(self):
        self.output = "M106" #Start Fan
        nozzleFirings = [0 for x in range(0, self.img.shape[1])]
        nozzleFirings = [copy.copy(nozzleFirings) for x in range(0, 4)]
        scan = range(0, self.img.shape[0])
        scan.reverse()
        for y in scan:
            for x in range(0, self.img.shape[1]):
                color = self.img[y,x]
                if color == self.black:
                    nozzleFirings[3][x] += 1 << y % self.nozzles
                else:
                    pass
            if y % 12 == 0 and y > 0:
                for headNumber, headVals in enumerate(nozzleFirings):
                    for column, firingVal in enumerate(headVals):
                        if firingVal:
                            #print(headNumber)
                            currentOffset = self.offsets
                            self.output += "G1 X"+str(self.increment*column-currentOffset[0])+" Y"+str(y/12*self.spread-currentOffset[1])+" F"+str(self.feedrate)+"\n"
                            self.output += "M400\n"
                            self.output += "M700 P"+str(headNumber)+" S"+str(firingVal)+"\n"
                            #print (self.output)
                nozzleFirings = [0 for x in range(0, self.img.shape[1])]
                nozzleFirings = [copy.copy(nozzleFirings) for x in range(0, 4)]
        f = open(self.outFile, 'w')
        f.write(self.output)
        f.close()

    def debug_to_terminal(self):
        print("Rows: "+str(self.img.shape[0]))
        print("Cols: "+str(self.img.shape[1]))
        print("Spread: "+str(self.spread)+"mm")
        print("Nozzles: "+str(self.nozzles))
        print("Print Area: "+str(self.printArea)+"mm")
        rowStr = ""
        for y in range(0, self.img.shape[0]):
            rowStr = ""
            for x in range(0, self.img.shape[1]):
                color = self.img[y, x]
                if color == self.black:
                    rowStr += " "
                else:
                    rowStr += termcolor.colored(" ", 'white', 'on_white')
            print (rowStr)


if __name__ == "__main__":
    #Setup Command line arguments
    parser = argparse.ArgumentParser(prog="image-to-gcode.py",
                                     usage="%(prog)s [options] input...",
                                     description="Convert bitmaps to gcode."
                                     )
    
    parser.add_argument("input",
                        help="input file, defaults to stdin"
                        )
    parser.add_argument('--version',
                        action='version',
                        version="%(prog)s 0.0.1-dev"
                        )


    #Always output help by default
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)  # Exit after help display
                                         
    args = parser.parse_args()
               
    imageProcessor = ImageToGcode(img=args.input,
                                  )

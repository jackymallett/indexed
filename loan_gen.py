# Plot amortization and payment of compound interest loans 
#
# (c) Jacky Mallett
#
# python loan_gen.py principal duration interest
#
import re, os
import sys
import gspread
import datetime as dt
import time
import locale
import numpy as np
from pylab import *
import matplotlib
from matplotlib.dates import date2num
import matplotlib.pyplot as plot
import matplotlib.axis   as axis
import matplotlib.mlab   as mlab
import matplotlib.cbook  as cbook
import matplotlib.ticker as ticker
import gchart as gc

DISPLAY = False

# Set font characteristics
rcParams['font.family']   ='Courier'
rcParams['axes.labelsize']= '10'
rcParams['font.size']     = '11'

# Calculate loan      

duration  = 480
principal = 200000

# 

J = float(sys.argv[1])/12			# Monthly interest
N = duration
P = principal

capital  = []
interest = []
payment  = []
step     = []
princ    = []

M = P * (J/(1 - pow(1 + J, N * -1)))
for i in range(1, duration+1):

    H = P * J		# Monthly Interest
    C = M - H       # Capital repayment
    Q = P - C       # New capital balance

    capital.append(C)
    interest.append(H)
    payment.append(M)
    step.append(i)
    princ.append(P)

    P = Q
 


# Colours for plotting

def getColour():
    for item in ['g', 'b', 'c','m','y','k','r']:
        yield item

# , formatting for y axis
def comma_format(num, places=0):
   locale.setlocale(locale.LC_ALL, "")
   return locale.format("%.0f",  num, True)

figure = plot.figure()
ax1    = subplot(111)
plot.suptitle("Fixed Rate, Compound interest Mortgage Schedule \n Principal = $%s %d years @ %.2f%%" %( comma_format(principal), duration/12, J*12*100))

plot.ylim(0)

plot.plot(step, princ  , marker='', color='black', ls='-')
ax2 = ax1.twinx()
plot.plot(step, payment, marker='', color='red', ls='-')

ax1.xaxis.set_major_locator(MaxNLocator(12))
ax1.yaxis.set_major_formatter(FuncFormatter(comma_format))
ax2.yaxis.set_major_formatter(FuncFormatter(comma_format))

if DISPLAY:
   plot.show()

print "Total paid = %d %d %d @ %f%%" % (sum(capital), sum(interest), sum(capital) + sum(interest), J*12*100)

figure.savefig("compound_%d_%d_%d.eps" %(principal, int(J*12*100),duration/12))

#!/usr/bin/python
#-*- coding: utf-8 -*-
# Chart the amortization table for an icelandic loan
# 
# optionally, include actual mortage index for stated period 
#
#    ice_graph principal interest year
import sys
import gspread
import datetime as dt
import time
import locale
import numpy as np
import matplotlib
#matplotlib.use('Agg')					# PNG file output
from pylab import *
from matplotlib.dates import date2num
import matplotlib.pyplot as plot
import matplotlib.axis   as axis
import matplotlib.mlab   as mlab
import matplotlib.cbook  as cbook
import matplotlib.ticker as ticker
import gchart as gc

DISPLAY = False

CPI       = 0.05		 # Default, fixed cpi
cpi_index = []			 # list of cpi indices as data
dates     = []
x_dates   = []

projectedDate  = -1       # Year from which values are extrapolated
projectedTitle = ""

# Base parameters for calculation (default values for sanity testing)

Principal = 10000000			# command line specified
Interest  = 0.04			    # command line specified
duration  = 480					# Use 480 for 40 year loans, 300 for 25, etc.

# Return the inflation rate for indexation. Can be specified as constant
# or read in from file on a per month basis

def getInflation(i):
    global projectedDate
    global projectedTitle

    if(len(cpi_index) == 0):
       inflation = pow((1.0 + CPI ),(1.0/12.0)) - 1
    else:
       if i < len(cpi_index):
          inflation = cpi_index[i]
       else:
          inflation = sum(cpi_index[-12:])/12 # Calculate average inflation/year
          # for 0% projections
          #inflation = 0
          x_dates.append(x_dates[-1] + 30) # Tack on month to dates array
                               
          if projectedDate == -1:             # store extrapolation year
             projectedDate = len(x_dates)-1
             
             projectedTitle = "\nProjected from 2011 with %d%% annual inflation rate" % (inflation * 12 * 100)
#          inflation = 0.0		              # for fixed rate charts
    return inflation

# , formatting function for matplotlib y axis
def comma_format(num, places=0):
   locale.setlocale(locale.LC_ALL, "")
   return locale.format("%.0f",  num, True)

# Chart information

# Set font characteristics
rcParams['font.family']   ='serif'
rcParams['axes.labelsize']= '10'
rcParams['font.size']     = '12'

# Specify spreadsheet 

username = 'threadneedleproject@gmail.com'
doc      = 'IcelandMortgageIndex'
p        = 'n33dle.2012'

#I         = Interest

D = float(30.0/360.0)

AF       = []			# Annuity factor
P        = []
payment  = []
interest = []
II       = []			# Inflation index
total    = 0		    # Total capital paid
P0       = []
increase = 0
capital_out = []		# Capital outstanding
paid     = []


# Determine whether fixed or supplied CPI rate should be used
# To use actual data, specify starting year. If period of loan is
# longer than data (which it will be for forty year loans) then the fixed 
# rate will be used for missing time periods

if(len(sys.argv) >= 2):
   Principal = int(float(sys.argv[1]) * 0.8)		# Use 80% of value
   Interest  = float(sys.argv[2])

if len(sys.argv) >= 4:
   # Attach to spreadsheet and get data

   gs          = gspread.login(username, p)
   spreadsheet = gs.open(doc)

   dates = spreadsheet.worksheet("IcelandIndex").col_values(1)
   index = gc.getSeries(3,"IcelandIndex", spreadsheet)

   start = 0
   for i in range(1, len(dates)):
       #print dates[i].split("-")[1], startYear
       if(dates[i].split("-")[1] == sys.argv[3]):
          start = i
          break
       
   for i in range(start, len(index)):
       if(index[i] == None): 
         cpi_index.append(0)
       else:
         cpi_index.append(float(index[i]))
       
       x_dates.append(date2num(dt.datetime.strptime(dates[i],'%B-%Y')))

if len(sys.argv) == 5:
   duration = int(sys.argv[4])
   years    = duration/12

# Compute payment last month in 2011

last2011 = date2num(dt.datetime.strptime("December-2011", '%B-%Y'))

# Compute Payments

# print "II     AF     P  "
for i in range(0, duration ):
  AF.append((1/(D*Interest) - 1/((D*Interest)*pow(1+D*Interest,duration-i))))

  if(i == 0):
    II.append(100 + 100 * getInflation(i))
    P.append(Principal * II[0]/100)
    increase = P[0] - Principal
  else:
    II.append(II[i-1] + II[i-1]*getInflation(i))
    P.append((P[i-1] - capital) * II[i]/II[i-1])
    increase = ((P[i-1] - capital) * II[i]/II[i-1]) - (P[i-1] - capital)

  payment     = P[i]/AF[i]
  interest    = P[i] * Interest * D
  capital     = payment - interest
  total       += capital

  paid.append(payment)
  capital_out.append(capital)

#  print "%0.1f %.2f %0.1f %0.1f %0.2f %0.1f  Inc:%0.1f" % (II[i],AF[i], P[i], payment, capital, interest, increase)


# Graph

figure = plot.figure(figsize=(12,8),dpi=100)
ax1    = subplot(111)
plot.suptitle(u'Verðtryggð lán Principal = %s ISK in %s @ %.1f%% base rate %s' 
              % (comma_format(Principal), sys.argv[3], Interest*100,projectedTitle), fontsize=13)
plot.ylim(0)

# Was any data projected forward
#print len(x_dates), len(P)
if projectedDate == -1:
   projectedDate = duration			    # Plot over duration of loan
   plot.plot_date(x_dates[0:projectedDate], P[0:projectedDate], 
                  label="Capital Outstanding", color='black',marker='', 
                  ls='-', lw=3.0)
   ax2 = ax1.twinx()
   plot.plot_date(x_dates[0:projectedDate], paid[0:projectedDate], 
                  label="Monthly payment", marker='', ls='-', lw=3.0,
                  color='red')
else:							        # Plot projected as a dashed line
   plot.plot_date(x_dates[0:projectedDate],P[0:projectedDate],  
                  label="Capital Outstanding", marker='', lw=3.0,
                  color='black',ls='-')
   plot.plot_date(x_dates[projectedDate:-1], P[projectedDate:-1], 
                  marker='', color='black',ls='--', lw=3.0)

   ax2 = ax1.twinx()
   plot.plot_date(x_dates[0:projectedDate], paid[0:projectedDate], 
                  label="Monthly payment", marker='', ls='-', lw=3.0,
                  color='red')
   plot.plot_date(x_dates[projectedDate:-1], paid[projectedDate:-1], 
                  marker='', ls='--', color='red', lw=3.0)

lines, labels   = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
legnd = legend(lines + lines2, labels + labels2, loc='upper left', fancybox=True)
legnd.get_frame().set_alpha(0.5)

ax1.set_ylabel("Capital Outstanding")
ax2.set_ylabel("Monthly Repayment")

ax1.xaxis.set_major_locator(MaxNLocator(12))
ax1.yaxis.set_major_formatter(FuncFormatter(comma_format))
ax2.yaxis.set_major_formatter(FuncFormatter(comma_format))

if DISPLAY:
   plot.show()

print "%s Total paid = %.2f" % (sys.argv[3], sum(paid))    

for i in range(0, len(paid)):
#    print x_dates[i], last2011
    if(x_dates[i] == last2011):
       print "12/2011 Repayment : " , paid[i]

print "Additional money = %d (max was %d)\n" %( max(P) - Principal, max(P))

figure.savefig(("fig_vl_%s_%s_%d.eps" % (sys.argv[1],sys.argv[3], years)),format="eps")

# Print out the amortization table for an icelandic loan
import sys

Principal = 20000000
Interest  = 0.04
duration  =  300        
I = Interest

D = float(30.0/360.0)

CPI = 0.05

inflation = pow((1.0 + CPI ),(1.0/12.0)) - 1
print inflation
AF = []
P = []
payment = []
interest = []
II = []
total = 0
negam = 0
P0 = []

tt = []  
increase = 0

print "II     AF     P  "
for i in range(0, duration ):
  AF.append((1/(D*I) - 1/((D*I)*pow(1+D*I,duration-i))))

  if(i == 0):
    II.append(100 + 100 * inflation)
    P.append(Principal * II[0]/100)
    increase = P[0] - Principal
  else:
    II.append(II[i-1] + II[i-1]*inflation)
    P.append((P[i-1] - capital) * II[i]/II[i-1])
    increase = ((P[i-1] - capital) * II[i]/II[i-1]) - (P[i-1] - capital)

  payment  = P[i]/AF[i]
  interest = P[i] * Interest * D
  capital  = payment - interest
  total += capital

  print "%0.1f %.2f %0.1f %0.1f %0.2f %0.1f  Inc:%0.1f" % (II[i],AF[i], P[i], payment, capital, interest, increase)

print "Capital paid = %.2f" % total


# Simple statistics script for merlin
# 
# Assumes that scan parsing logs are stored in "scanlog.txt" and excalibur logs in "dumplog.txt".
# 
# Martin Stone

from numpy import mean, std, var

f=file("scanlog.txt","r")
a=[]
for l in f:              
     if l[:5] == "Total":   
         a.append(float(l.split()[3]))
print("Scan parsing times:")
print("    Min: %5.3fs  Max: %5.3fs  Mean: %5.3fs  Standard Deviation: %5.3fs  Variance: %5.3fs  Samples: %d" % (min(a), max(a), mean(a), std(a), var(a), len(a)))
f.close()

f=file("dumplog.txt","r")
a=[]
b=[]
for l in f:              
     if l[:7] == "Total t":   
         a.append(float(l.split()[3]))
     elif l[:6] == "Loaded":
         b.append(float(l.split()[5]))
print("Dump loading times:")
print("    Min: %5.3fs  Max: %5.3fs  Mean: %5.3fs  Standard Deviation: %5.3fs  Variance: %5.3fs  Samples: %d" % (min(b), max(b), mean(b), std(b), var(b), len(b)))
print("Total tick processing times:")
print("    Min: %5.3fs  Max: %5.3fs  Mean: %5.3fs  Standard Deviation: %5.3fs  Variance: %5.3fs  Samples: %d" % (min(a), max(a), mean(a), std(a), var(a), len(a)))
f.close()

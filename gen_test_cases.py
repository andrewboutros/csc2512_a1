from random import seed
from random import randint
import random

seed(1)

n = 100

S_start = 10
S_end = 10
S_step = 15

k_start = 10
k_end = 100
k_step = 10

numc_start = 1
numc_end = 10
numc_step = 1

# Sweep S
k = k_start
numc = numc_start
for S in range(S_start, S_end+1, S_step):
	f = open("test_cases/test_" + str(S) + "_" + str(k) + "_" + str(numc), "w")
	f.write("0\n")
	f.write(str(numc)+"\n")
	for c in range(numc):
		elements = random.sample(range(1, n), S)
		signs = [random.randint(0,10) for i in range(S)]
		for i in range(S):
			if(signs[i] == 0):
				f.write(str(elements[i]) + " ")
			else:
				f.write(str(-1 * elements[i]) + " ")
		f.write("\n")

		f.write("0 " + str(k) + "\n")

	f.close()
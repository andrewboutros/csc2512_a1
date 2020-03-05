from random import seed
from random import randint
import random
import os

def sweep_constrained_literals(S_start, S_end, S_step, mu, k, num_constraints, minisat_path, log):
	
	for S in range(S_start, S_end+1, S_step):

		# --------------------------- Generate test case -----------------------------
		upper_bound = int(k * S)
		lower_bound = int(mu * S)
		test_case_name = "test_" + str(S) + "_" + str(lower_bound) + "_" + str(upper_bound) + "_" + str(num_constraints)
		f = open("test_cases/" + test_case_name, "w")

		# Total number of variables (n) is equal to the sum of variable counts of all contraints
		n = S * num_constraints;
		f.write(str(n)+"\n")
		f.write(str(num_constraints)+"\n")

		# Write the cardinality constraints
		for c in range(num_constraints):
			# Pick "S" random numbers from the range [1, n] without repetition and random signs (-1 or 1)
			elements = random.sample(range(1, n+1), S)
			signs = [random.choice([-1, 1]) for i in range(S)]

			# Write the literals of the constraint
			for i in range(S):
			    f.write(str(signs[i] * elements[i]) + " ")
			f.write("\n")

			# Write the lower and upper bounds
			f.write(str(lower_bound) + " " + str(upper_bound) + "\n")
		f.close()

		# ---------------------------- Encode test case ------------------------------
		os.system("./encoding test_cases/" + test_case_name + " dimacs/" + test_case_name + ".dimacs >> reports/" + test_case_name + "_encoding.rpt")
		
		# --------------------------- Run Minisat Solver -----------------------------
		os.system(minisat_path + "/bin/minisat dimacs/" + test_case_name + ".dimacs outputs/" + test_case_name + ".out >> reports/" + test_case_name + "_minisat.rpt")

		# Print Results
		with open("reports/" + test_case_name + "_minisat.rpt") as report:
			sat = "UNSAT"
			for line in report:
				line = line.rstrip()
				if "SATISFIABLE" in line:
					sat = "SAT"
				if "CPU time" in line:
					line = line.split(":")
					solver_time = line[1].split(" ")

		with open("reports/" + test_case_name + "_encoding.rpt") as report:
			clauses = 0
			variables = 0
			for line in report:
				line = line.rstrip()
				if "Constructing totalizer clauses" in line:
					line = line.split(" ")
					clauses += int(line[7])
				if "Constructing comparator clauses" in line:
					line = line.split(" ")
					clauses += int(line[7])
				if "Number of extra" in line:
					line = line.split(" ")
					variables += int(line[6])
				if "Total Encoding" in line:
					line = line.split(" ")
					encoding_time = line[4]

		print('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % (S, lower_bound, upper_bound, num_constraints, sat, solver_time[1], variables, clauses, encoding_time))
		log.write(('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % (S, lower_bound, upper_bound, num_constraints, sat, solver_time[1], variables, clauses, encoding_time)) + "\n")


def main(minisat_path):
	S_start = 100 
	S_end = 6000
	S_step = 100

	num_constraints = 1
	log = open("log", "w")

	print((16*9+10) * "-")
	log.write(((16*9+10) * "-") + "\n")

	print('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % ("S", "MU", "K", "NUM_C", "OUTPUT", "SOLVER TIME (S)", "VARIABLES", "CLAUSES", "ENC TIME (S)"))
	log.write(('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % ("S", "MU", "K", "NUM_C", "OUTPUT", "SOLVER TIME (S)", "VARIABLES", "CLAUSES", "ENC TIME (S)")) + "\n")

	print((16*9+10) * "-")
	log.write(((16*9+10) * "-") + "\n")
	for k in range(20, 90, 10):
		sweep_constrained_literals(S_start, S_end, S_step, 0, (1.0*k)/100.0, num_constraints, minisat_path, log)
	print((16*9+10) * "-")
	log.write(((16*9+10) * "-") + "\n")


minisat_path = "/home/andrew/2020_winter/csc2512/minisat"
os.system("rm test_cases/* dimacs/* reports/*")
seed(1)
main(minisat_path)
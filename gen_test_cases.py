from random import seed
from random import randint
import random
import os

def verify_correctness(solution_file, problem_file):
	with open(solution_file) as solution:
		sol = solution.readlines()[0]
		if("UNSAT" in sol):
			return True

	with open(solution_file) as solution:
		file = solution.readlines()[1:]
		truth_assignment = file[0].rstrip().split(" ")
		for t in range(len(truth_assignment)):
			truth_assignment[t] = int(truth_assignment[t])

	with open(problem_file) as problem:
		constraints = problem.readlines()[2:]
		for i in range(len(constraints)):
			constraints[i] = constraints[i].rstrip().split(" ")
			for j in range(len(constraints[i])):
				constraints[i][j] = int(constraints[i][j])

	all_good = True
	for i in range(0, len(constraints), 2):
		count = 0
		for j in range(len(constraints[i])):
			idx = constraints[i][j]
			pos = 1
			if(constraints[i][j] < 0):
				idx = idx * -1
				pos = 0
			if((truth_assignment[idx-1] < 0 and pos == 0) or (truth_assignment[idx-1] > 0 and pos == 1)):
				count = count + 1
		if not((count >= constraints[i+1][0]) and (count <= constraints[i+1][1])):
			all_good = False
			break
	
	return all_good

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
			elements = random.sample(range(1, int(((1.0+(1.0*c/5))*S))+1), S)
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

		# --------------------------- Verify Solver Output -----------------------------
		correct = verify_correctness("outputs/"+test_case_name+".out", "test_cases/"+test_case_name)

		# --------------------------- Print Results Summary ----------------------------
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

		if(correct):
			correct_text = "YES"
		else:
			correct_text = "NO"

		print('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % (S, lower_bound, upper_bound, num_constraints, sat, solver_time[1], variables, clauses, encoding_time, correct_text))
		log.write(('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % (S, lower_bound, upper_bound, num_constraints, sat, solver_time[1], variables, clauses, encoding_time, correct_text)) + "\n")


def main(minisat_path):
	S_start = 100 
	S_end = 1200
	S_step = 100

	num_constraints = 1
	log = open("log", "w")

	print((16*10+11) * "-")
	log.write(((16*10+11) * "-") + "\n")

	print('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % ("S", "MU", "K", "NUM_C", "OUTPUT", "SOLVER TIME (S)", "VARIABLES", "CLAUSES", "ENC TIME (S)", "CORRECT?"))
	log.write(('|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|%-16s|' % ("S", "MU", "K", "NUM_C", "OUTPUT", "SOLVER TIME (S)", "VARIABLES", "CLAUSES", "ENC TIME (S)", "CORRECT?")) + "\n")

	print((16*10+11) * "-")
	log.write(((16*10+11) * "-") + "\n")
	
	# Sweep |S| and k
	for k in range(20, 90, 20):
		sweep_constrained_literals(S_start, S_end, S_step, 0, (1.0*k)/100.0, num_constraints, minisat_path, log)

	# Sweep C
	for c in range(1, 21, 2):
		sweep_constrained_literals(1000, 1000, 100, 0, 0.4, c, minisat_path, log)

	print((16*10+11) * "-")
	log.write(((16*10+11) * "-") + "\n")


minisat_path = "/home/andrew/2020_winter/csc2512/minisat"
#os.system("rm test_cases/* dimacs/* reports/*")
seed(1)
main(minisat_path)





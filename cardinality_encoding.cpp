#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include "node.cpp"

using namespace std;

template <typename T> 
ostream& operator<<(ostream& os, const vector<T>& v) 
{ 
    os << "["; 
    for (int i = 0; i < v.size(); ++i) { 
        os << v[i]; 
        if (i != v.size() - 1) 
            os << ", "; 
    } 
    os << "]"; 
    return os; 
} 

ostream& operator<<(ostream& os, const Node& n) 
{ 
    os << "({"; 
    for (int i = 0; i < n.variables.size(); ++i) { 
        os << n.variables[i]; 
        if (i != n.variables.size() - 1) 
            os << ", "; 
    } 
    os << "}, ";
    os << n.label << ")"; 
    return os; 
} 

Node* build_tree(vector<int> literals, int* used_literal, int* added_literal, int label, int* node_id){
	Node* n = new Node(*node_id, label);
	cout << "Created node N" << *node_id << ": ";
	(*node_id)++;
	if(label == 1){
		n->variables.push_back(literals[*used_literal]);
		(*used_literal)++;
		cout << *n << endl;
		return n;
	} else {
		for(unsigned int i = 0; i < label; i++){
			n->variables.push_back(*added_literal);
			(*added_literal)++;
		}
		cout << *n << endl;
		n->left_child = build_tree(literals, used_literal, added_literal, label/2, node_id);
		n->right_child = build_tree(literals, used_literal, added_literal, label-(label/2), node_id);
		return n;
	}
}

void construct_totalizer(Node* n, vector<vector<int>>* clauses){
	int m1 = n->left_child->variables.size();
	int m2 = n->right_child->variables.size();
	int m = n->label;

	// Construct totalizer clauses for current node
	for(unsigned int alpha = 0; alpha <= m1; alpha++){
		for(unsigned int beta = 0; beta <= m2; beta++){
			unsigned int sigma = alpha + beta;
			if(sigma <= m){
				vector<int> c1, c2;
				// Construct first clause
				if(sigma != 0) {
					c1.push_back(n->variables[sigma-1]);
					if(alpha != 0) { c1.push_back(-1 * n->left_child->variables[alpha-1]); }
					if(beta != 0)  { c1.push_back(-1 * n->right_child->variables[beta-1]); }
					clauses->push_back(c1);
					cout << "(-a" << alpha << ", -b" << beta << ", r" << sigma << "): " << c1 << endl;
				}
				
				// Construct second clause
				if(sigma + 1 <= m){
					c2.push_back(-1 * n->variables[sigma]);
					if(alpha + 1 <= m1) { c2.push_back(n->left_child->variables[alpha]); }
					if(beta + 1 <= m2)  { c2.push_back(n->right_child->variables[beta]); }
					clauses->push_back(c2);
					cout << "(a" << alpha+1 << ", b" << beta+1 << ", -r" << sigma+1 << "): " << c2 << endl;
				}					
			}
		}
	}

	// Construct clauses recursively for children as long as their label is > 1
	if(n->left_child->label > 1)
		construct_totalizer(n->left_child, clauses);
	if(n->right_child->label > 1)
		construct_totalizer(n->right_child, clauses);
}

void construct_comparator(vector<int>* output_variables, vector<vector<int>>* clauses, int lower_bound, int upper_bound){
	vector<int> temp(1);
	// Add s_i
	for(unsigned int i = 0; i < lower_bound; i++){
		temp[0] = output_variables->at(i);
		clauses->push_back(temp);
	}

	// Add s_j
	for(unsigned int j = upper_bound; j < output_variables->size(); j++){
		temp[0] = -1 * output_variables->at(j);
		clauses->push_back(temp);
	}
}

int encode_constraint(vector<int> literals, int lower_bound, int upper_bound, int start_variable, vector<vector<int>>* encoding)
{
	int var = start_variable;
	int used_literal = 0;
	int node_id = 0;

	// Build binary tree
	cout << "[INFO] Building binary tree" << endl;
	Node* root = build_tree(literals, &used_literal, &var, literals.size(), &node_id);
	cout << "[INFO] Tree built successfully!" << endl;
	cout << "**********************************************************" << endl;

	// Construct totalizer clauses
	cout << "[INFO] Constructing totalizer clauses" << endl;
	construct_totalizer(root, encoding);
	int num_totalizer_clauses = encoding->size();
	cout << "[INFO] A total of " << num_totalizer_clauses << " totalizer clauses constucted successfully!" << endl;
	cout << "**********************************************************" << endl;

	// Construct comparator clauses
	cout << "[INFO] Constructing comparator clauses" << endl;
	construct_comparator(&(root->variables), encoding, lower_bound, upper_bound);
	int num_comparator_clauses = encoding->size() - num_totalizer_clauses;
	cout << "[INFO] A total of " << num_comparator_clauses << " comparator clauses constucted successfully!" << endl;
	cout << "**********************************************************" << endl;

	return (var - start_variable + 1);
}

void dump_dimacs_file(vector<vector<int>> *encoding, int num_encoding_variables, char *encoding_filename)
{
	ofstream encoding_file;
	encoding_file.open(encoding_filename);
	encoding_file << "p cnf " << num_encoding_variables << " " << encoding->size() << endl;
	for(unsigned int i = 0; i < encoding->size(); i++){
		for(unsigned int j = 0; j < encoding->at(i).size(); j++){
			encoding_file << encoding->at(i).at(j) << " ";
		}
		encoding_file << "0" << endl;
	}
}

int main(int argc, char* argv[])
{
	// Make sure the user specified constraints file
	if(argc < 3){
		cout << "[ERROR] Please specify cardinality constraints file name and output file name" << endl;
		return 0;
	}

	// Open constraints file
	ifstream constraints_file;
	string line;
	constraints_file.open(argv[1]);
	if(!constraints_file){
		cout << "[ERROR] Unable to open constraints file" << endl;
		return 0;
	}
	
	cout << "**********************************************************" << endl;
	cout << "[INFO] Started parsing input file" << endl;
	// Get number of variables in the original problem
	int num_variables;
	if(getline(constraints_file, line)){
		num_variables = stoi(line);
		cout << "[INFO] The original problem has " << num_variables << " variables." << endl;
	} else {
		cout << "[ERROR] Input file is empty" << endl;
		return 0;
	}


	// Get number of cardinality constrained specified in the input file
	int num_constraints;
	if(getline(constraints_file, line)){
		num_constraints = stoi(line);
		cout << "[INFO] A total of " << num_constraints << " cardinality constraint(s) are specified in the input file." << endl;
	} else {
		cout << "[ERROR] Input file format is invalid! Refer to the README file for more information about the input file format" << endl;
		return 0;
	}
	
	// Parse cardinality constraints 
	int num_parsed_constraints = 0;
	vector<vector<int>> literals;
	vector<int> lower_bounds;
	vector<int> upper_bounds;
	int num_line = 0;
	int temp;
	while(getline(constraints_file, line)){
		stringstream linestream;
		linestream.str(line);
		if(num_line == 0){
			// Parse the set of literals in the sum (S)
			vector<int> constraint;
			while(linestream >> temp){
				constraint.push_back(temp);
			}
			literals.push_back(constraint);
			num_line++;
		} else {
			// Parse constraint lower bound (u)
			linestream >> temp;
			lower_bounds.push_back(temp);
			
			// Parse constraint upper bound (k)
			linestream >> temp;
			upper_bounds.push_back(temp);

			num_line = 0;
			num_parsed_constraints++;
		}
	}
	
	if(num_parsed_constraints < num_constraints){
		cout << "[ERROR] Input file format is invalid! Refer to the README file for more information about the input file format" << endl;
		return 0;
	}

	cout << "Literals of cardinality constraints: " << literals << endl;
	cout << "Lower bounds: " << lower_bounds << endl;
	cout << "Upper bounds: " << upper_bounds << endl;
	cout << "[INFO] Parsing of input file finished successfully!" << endl;
	cout << "**********************************************************" << endl;
	
	vector<vector<int>> encoding;
	int constraint_encoding_start = num_variables + 1;
	int num_encoding_variables = 0;
	for(unsigned int i = 0; i < num_constraints; i++){
		num_encoding_variables += encode_constraint(literals[i], lower_bounds[i], upper_bounds[i], constraint_encoding_start, &encoding);
		constraint_encoding_start = num_variables + num_encoding_variables;
	}

	dump_dimacs_file(&encoding, num_encoding_variables+num_variables, argv[2]);

	cout << "[INFO] Encoding process finished successfully!" << endl;
	return 1;
}

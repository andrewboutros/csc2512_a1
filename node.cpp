#include <iostream>
#include <vector>

using namespace std;

class Node {
	public:
		int node_id;
		vector<int> variables;
		int label;
		Node* left_child;
		Node* right_child;

		Node(int node_id, int label){
			this->node_id = node_id;
			this->label = label;
		}
};



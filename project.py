import time
import math

from operator import attrgetter

leafEnd = -1
class SuffixNode:
    """The Suffix-tree's node."""

    def __init__(self, leaf):
        self.children = {}
        self.leaf = leaf
        self.index = None
        self.start = None
        self.end = None
        self.link = None

    # Helper function to compare equality two suffix nodes
    def __eq__(self, node):
        atg = attrgetter('start', 'end', 'index')
        return atg(self) == atg(node)

    # Helper function to compare equality two suffix nodes
    def __ne__(self, node):
        atg = attrgetter('start', 'end', 'index')
        return atg(self) != atg(node)

    def __getattribute__(self, name):
        if name == 'end':
            if self.leaf:
                return leafEnd
        return super(SuffixNode, self).__getattribute__(name)


class SuffixTree:
    """The Suffix-Tree."""

    def __init__(self, data):
        self._string = data
        self.last_node_for_suffix_link = None
        self.active_node = None
        self.active_edge = -1
        self.active_length = 0
        self.remaining = 0
        self.root_end = None
        self.split_end = None
        self.length_of_input = -1  
        self.root = None

    def get_edge_length(self, node):
        return node.end - node.start + 1

    def walk_down(self, current_node):
        """Walk down from current node."""
        length = self.get_edge_length(current_node)
        if (self.active_length >= length):
            self.active_edge += length
            self.active_length -= length
            self.active_node = current_node
            return True
        return False

    def new_node(self, start, end=None, leaf=False):
        node = SuffixNode(leaf)
        node.link = self.root
        node.start = start
        node.end = end
        node.index = -1
        return node

    def extend_suffix_tree(self, pos):
        global leafEnd
        
        # Rule 1
        leafEnd = pos
        
        # Track number of suffixes to be added
        self.remaining += 1
        
        # Initially suffix link is empty
        self.last_node_for_suffix_link = None

        # Loop through the remaining links
        while(self.remaining > 0):
            if (self.active_length == 0):
                self.active_edge = pos  
            if (self.active_node.children.get(self._string[self.active_edge]) is None):
                # Rule 2
                self.active_node.children[self._string[self.active_edge]] = self.new_node(pos, leaf=True)
                # Set last node for suffix link's link to current node
                # Set current nodes link to none
                if (self.last_node_for_suffix_link is not None):
                    self.last_node_for_suffix_link.link = self.active_node
                    self.last_node_for_suffix_link = None
            else:
                # Get the next node
                _next = self.active_node.children.get(self._string[self.active_edge])

                # Walkdown until active_node
                if self.walk_down(_next):  
                    continue
                

                if (self._string[_next.start + self.active_length] == self._string[pos]):
                    # Set last node for suffix link's link to current node
                    # Set current nodes link to none
                    if((self.last_node_for_suffix_link is not None) and (self.active_node != self.root)):
                        self.last_node_for_suffix_link.link = self.active_node
                        self.last_node_for_suffix_link = None
                    
                    # Move to next character
                    self.active_length += 1
                    
                    # Trick 3 Break the current phase
                    break
                
                # Create new Internal node and associate link
                self.split_end = _next.start + self.active_length - 1

                # New internal node
                split = self.new_node(_next.start, self.split_end)
                self.active_node.children[self._string[self.active_edge]] = split

                # New leaf coming out of new internal node
                split.children[self._string[pos]] = self.new_node(pos, leaf=True)
                _next.start += self.active_length
                split.children[self._string[_next.start]] = _next

                # Check if any internal node created has link to root
                if (self.last_node_for_suffix_link is not None):
                    # If yes connect to current node
                    self.last_node_for_suffix_link.link = split
                
                self.last_node_for_suffix_link = split
            
            # Finished processing
            self.remaining -= 1

            if ((self.active_node == self.root) and (self.active_length > 0)):  
                self.active_length -= 1
                self.active_edge = pos - self.remaining + 1
            elif (self.active_node != self.root):  
                self.active_node = self.active_node.link

    def dfs(self, current):
        start, end = current.start, current.end
        yield self._string[start: end + 1]

        for node in current.children.values():
            if node:
                yield from self.dfs(node)

    def build(self):
        self.length_of_input = len(self._string)

        """Root is a special node with start and end indices as -1,
        as it has no parent from where an edge comes to root"""
        self.root_end = -1
        self.root = self.new_node(-1, self.root_end)
        self.active_node = self.root  # First active_node will be root
        for i in range(self.length_of_input):
            self.extend_suffix_tree(i)

    def __str__(self):
        return "\n".join(map(str, self.edges.values()))

    def print_dfs(self):
        for sub in self.dfs(self.root):
            print(sub)

def find_all_inner_nodes(node, traversed_edges):
    for char, child in node.children.items():
        if child.leaf:
            yield child.start - traversed_edges
        else:
            start, end = child.start, child.end
            pattern_length = end - start + 1
            yield from find_all_inner_nodes(child, traversed_edges + pattern_length)

def find_all_match( node, actual_pattern_length,pattern_length):
    if node.leaf:
        first = node.start - (actual_pattern_length - pattern_length)
        return [first, *find_all_inner_nodes(node, actual_pattern_length)]
    else:
        return list(find_all_inner_nodes(node, actual_pattern_length))
    
def check_for_suffix(actual_string:str,root:SuffixNode,pattern:str,find_all:bool):
    pattern_length = len(pattern)
    item = next(((char, child) for char, child in root.children.items() if pattern.startswith(char)), None)
    if item:
        char, child = item
        start, end = child.start, child.end
        if actual_string[start: end + 1].startswith(pattern):
            if find_all:
                return find_all_match(child, len(pattern),len(pattern))
            return start - (pattern_length - len(pattern))
        return check_for_suffix(actual_string,child, pattern[end - start + 1:],find_all)
    else:
        return -1


def main(input_string,pattern):
    input_string+="$"
    start = time.time_ns()
    tree = SuffixTree(input_string)
    tree.build()
    check = check_for_suffix(input_string,tree.root,pattern,True)
    end = time.time_ns()
    duration = end-start
    duration_in_ms = duration/pow(10,6)
    text_ = ""
    if check == -1:
        text_ = "Pattern: \""+pattern+"\"\n\nInput:     \""+input_string[:-1]+"\"\n\nResult:   No match"
    else:
        text_ = "Pattern: \""+pattern+"\"\n\nInput:     \""+input_string[:-1]+"\"\n\nIndices: [ "
        text_+= ' , '.join(map(str, check)) 
        text_+=" ]\n\n"
        text_+="Duration: "+str(duration_in_ms)+" ms\n"
    return {
        "duration":duration_in_ms,
        "results":None if check == -1 else check,
        "value":text_
    }



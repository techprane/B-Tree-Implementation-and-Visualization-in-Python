from graphviz import Digraph

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

    def display(self, level=0):
        print("Level", level, ":", self.keys)
        if not self.leaf:
            for child in self.children:
                child.display(level + 1)

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t

    def find(self, k, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and k == node.keys[i]:
            return node, i
        elif node.leaf:
            return None
        else:
            return self.find(k, node.children[i])

    def insert(self, k):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            new_root = BTreeNode(self.t, False)
            new_root.children.append(self.root)
            self.root = new_root
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, k)
        else:
            self._insert_non_full(root, k)

    def _insert_non_full(self, node, k):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(0)
            while i >= 0 and k < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = k
        else:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t) - 1:
                self._split_child(node, i)
                if k > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], k)

    def _split_child(self, parent, i):
        t = self.t
        node = parent.children[i]
        new_node = BTreeNode(t, node.leaf)
        parent.keys.insert(i, node.keys[t - 1])
        parent.children.insert(i + 1, new_node)
        new_node.keys = node.keys[t:(2 * t) - 1]
        node.keys = node.keys[0:t - 1]
        if not node.leaf:
            new_node.children = node.children[t:(2 * t)]
            node.children = node.children[0:t]

    def delete(self, k, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and k > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == k:
            if node.leaf:
                node.keys.pop(i)
            else:
                if len(node.children[i].keys) >= self.t:
                    node.keys[i] = self._get_pred(node.children[i])
                    self.delete(node.keys[i], node.children[i])
                elif len(node.children[i + 1].keys) >= self.t:
                    node.keys[i] = self._get_succ(node.children[i + 1])
                    self.delete(node.keys[i], node.children[i + 1])
                else:
                    self._merge(node, i)
                    self.delete(k, node.children[i])
        elif not node.leaf:
            if len(node.children[i].keys) < self.t:
                self._fill(node, i)
            self.delete(k, node.children[i])

    def _get_pred(self, node):
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _get_succ(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0]

    def _merge(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]
        child.keys.append(node.keys[i])
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        node.keys.pop(i)
        node.children.pop(i + 1)
        if node == self.root and len(node.keys) == 0:
            self.root = child

    def _fill(self, node, i):
        if i != 0 and len(node.children[i - 1].keys) >= self.t:
            self._borrow_from_prev(node, i)
        elif i != len(node.children) - 1 and len(node.children[i + 1].keys) >= self.t:
            self._borrow_from_next(node, i)
        else:
            if i != len(node.children) - 1:
                self._merge(node, i)
            else:
                self._merge(node, i - 1)

    def _borrow_from_prev(self, node, i):
        child = node.children[i]
        sibling = node.children[i - 1]
        child.keys.insert(0, node.keys[i - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        node.keys[i - 1] = sibling.keys.pop()

    def _borrow_from_next(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]
        child.keys.append(node.keys[i])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        node.keys[i] = sibling.keys.pop(0)

    def update(self, old_key, new_key):
        result = self.find(old_key)
        if result is not None:
            node, i = result
            node.keys[i] = new_key
        else:
            print("Key to update not found.")

    def display(self):
        self.root.display()

    def visualize(self):
        dot = Digraph()
        self._add_nodes_edges(dot, self.root)
        dot.render("btree", view=True, format="png")

    def _add_nodes_edges(self, dot, node, parent_id=None):
        node_id = str(id(node))
        label = " | ".join(map(str, node.keys))
        dot.node(node_id, label=label, shape="record")
        if parent_id:
            dot.edge(parent_id, node_id)
        if not node.leaf:
            for child in node.children:
                self._add_nodes_edges(dot, child, node_id)

# Usage example:
if __name__ == "__main__":
    b_tree = BTree(t=2)
    for key in [10, 20, 5, 6, 12, 30, 7, 17, 4, 15, 1]:
        b_tree.insert(key)
    
    print("B-Tree structure:")
    b_tree.display()

    # Test find operation and print result
    key_to_find = 15
    result = b_tree.find(key_to_find)
    if result:
        node, index = result
        print(f"\nKey {key_to_find} found in node with keys: {node.keys}")
    else:
        print(f"\nKey {key_to_find} not found in the B-Tree.")

    # Testing delete operation
    b_tree.delete(6)
    print("\nAfter deleting 6:")
    b_tree.display()

    # Visualize the B-Tree structure
    b_tree.visualize()
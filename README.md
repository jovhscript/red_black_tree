This is a library for creating and storing immutable red-black binary search trees. Red-black trees are similar to ordinary binary search trees, but rebalance every time a node is inserted. Deletion is not currently supported in this software. The implemented technique guarantees reading and inserting in O(log n) time, and abides by the following four balancing rules, assuming each node is assigned either a Red or Black colour:

1) The root node is black.
2) No red node can be the child of another red node.
3) The black depth (distance between root node and deepest black node) is consistent across the tree
4) Every bottom-rung leaf is black.

In the event that one of these rules is violated, the tree is rebalanced according to three main protocols: left-rotation, right-rotation, and recoloring. Rotation ensures the depth-balance of the tree while recoloring recalibrates the tree for further insertions and reads of the tree. Our library contains the following 3 files:

1) immutable_tree.py contains an implementation of the immutable BST adapted from Lab 10.
2) red_black_tree.py contains an implementation of the Red-Black tree adapted from http://scottlobdell.me/2016/02/purely-functional-red-black-trees-python/
3) test_tree.py contains a series of unit tests for both the immutable BST class and red_black_tree class.

CONTRIBUTORS:

The primary authors of this library are Virgile Audi, Omar Abboud, Jack Qian, and Heidi Chen. This library was created as part of course CS207 - Systems Development for Computational Science at the Harvard University Institute for Applied Computational Science.
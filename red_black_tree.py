from immutable_tree import *
import os

class Color(object):
    RED = 0
    BLACK = 1

class RedBlackNodeRef(ValueRef):
    " a reference to a string value on disk"
    def __init__(self, referent=None, address=0):
        self._referent = referent #value to store
        self._address = address #address to store at

    "reference to a btree node on disk"

    #calls the BinaryNode's store_refs
    def prepare_to_store(self, storage):
        "have a node store its refs"
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_bytes(referent):
        "use pickle to convert node to bytes"
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
            'color': referent.color
        })

    @staticmethod
    def bytes_to_referent(string):
        "unpickle bytes to get a node object"
        d = pickle.loads(string)
        return RedBlackNode(
            RedBlackNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            RedBlackNodeRef(address=d['right']),
            d['color']
        )


class RedBlackNode(BinaryNode):

    @classmethod
    def from_node(cls, node, **kwargs):
        "clone a node with some changes from another one"
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
            color=kwargs.get('color', node.color),
        )

    def __init__(self, left_ref, key, value_ref, right_ref, color=Color.RED):
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color

    def is_black(self):
        return self.color == Color.BLACK

    def is_red(self):
        return self.color == Color.RED

    def is_empty(self):
        return False


class RedBlackTree(BinaryTree):

    def _refresh_tree_ref(self):
        "get reference to new tree if it has changed"
        self._tree_ref = RedBlackNodeRef(
            address=self._storage.get_root_address())

    def is_empty(self):
        return False

    def _blacken(self, node):
        #node = self._follow(ref)
        if node is None:
            return node
        newnode = RedBlackNode.from_node(node, color=Color.BLACK)
        return RedBlackNodeRef(newnode)

    def rootkey(self):
        return self._follow(self._tree_ref).key

    def rotate_left(self, node):
        right = self._follow(node.right_ref)
        if self._follow(right.left_ref) is not None:
            newleft_right = RedBlackNode.from_node(self._follow(right.left_ref),
                                                   left_ref = RedBlackNodeRef(),
                                                   right_ref = RedBlackNodeRef(),
                                                   color = node.color)
            newleft_right_ref = RedBlackNodeRef(referent = newleft_right)
        else:
            newleft_right_ref = RedBlackNodeRef()
        newleft = RedBlackNode.from_node(node, 
                                         right_ref = newleft_right_ref)
        newnode = RedBlackNode.from_node(right,
                                         left_ref = RedBlackNodeRef(referent=newleft))
        return newnode


    def rotate_right(self, node):
        left = self._follow(node.left_ref)
        if self._follow(left.right_ref) is not None:
            newright_left = RedBlackNode.from_node(self._follow(left.right_ref),
                                                   left_ref = RedBlackNodeRef(),
                                                   right_ref = RedBlackNodeRef(),
                                                   color = node.color)
            newright_left_ref = RedBlackNodeRef(referent = newleft_right)
        else:
            newright_left_ref = RedBlackNodeRef()
                                        
        newright = RedBlackNode.from_node(node, 
                                          left_ref = newright_left_ref)
        newnode = RedBlackNode.from_node(left,
                                         right_ref = RedBlackNodeRef(referent=newright))

        return newnode
                                      
    def recolor(self, node):
        left = self._blacken(self._follow(node.left_ref))
        right = self._blacken(self._follow(node.right_ref))

        return RedBlackNode.from_node(node, 
                                      left_ref = left,
                                      right_ref = right,
                                      color=Color.RED)

    def _isred(self, node):
        if node is None:
            return False
        else:
            return node.color == Color.RED

    def balance(self, node):

        if self._isred(node) | (node is None):
            return node

        left = self._follow(node.left_ref)
        right = self._follow(node.right_ref)

        if self._isred(left):
            if self._isred(right):
                return self.recolor(node)
            if self._isred(self._follow(left.left_ref)):
                return self.recolor(self.rotate_right(node))
            if self._isred(self._follow(left.right_ref)):
                newleft = self.rotate_left(left)
                newnode = RedBlackNode.from_node(node, 
                                                 left_ref = RedBlackNodeRef(referent = newleft))
                return self.recolor(self.rotate_right(newnode))
        if self._isred(right):
            if self._isred(self._follow(right.right_ref)):
                return self.recolor(self.rotate_left(node))
            if self._isred(self._follow(right.left_ref)):
                newright = self.rotate_right(right)
                newnode = RedBlackNode.from_node(node, 
                                                 right_ref = RedBlackNodeRef(referent = newright))
                return self.recolor(self.rotate_left(newnode))

        return node
        
                

    def set(self, key, value):
        "set a new value in the tree. will cause a new tree"
        #try to lock the tree. If we succeed make sure
        #we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        #get current top-level node and make a value-ref
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        #insert and get new tree ref
        self._tree_ref = self._insert(node, key, value_ref)
        self._tree_ref = self._blacken(self._follow(self._tree_ref))


    def _insert(self, node, key, value_ref):
        "insert a new node creating a new path from root"
        #create a tree if there was none so far
        if node is None:
            #print ('a')
            new_node = RedBlackNode(
               RedBlackNodeRef(), key, value_ref, RedBlackNodeRef())
        elif key < node.key:
            newleft_ref = self._insert(self._follow(node.left_ref), key, value_ref)
            newleft = self.balance(self._follow(newleft_ref))
            new_node = self.balance(RedBlackNode.from_node(
                    node,
                    left_ref=RedBlackNodeRef(referent=newleft)))
        elif key > node.key:
            newright_ref = self._insert(self._follow(node.right_ref), key, value_ref)
            newright = self.balance(self._follow(newright_ref))
            new_node = self.balance(RedBlackNode.from_node(
                    node,
                    right_ref=RedBlackNodeRef(referent=newright)))
        else: #create a new node to represent this data
            new_node = RedBlackNode.from_node(node, value_ref=value_ref)
        #new_node = self._blacken(new_node)
        return RedBlackNodeRef(referent=new_node)


def connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)


class DBDB(object):

    def __init__(self, f):
        self._storage = Storage(f)
        self._tree = RedBlackTree(self._storage)

    def _assert_not_closed(self):
        if self._storage.closed:
            raise ValueError('Database closed.')

    def close(self):
        self._storage.close()

    def commit(self):
        self._assert_not_closed()
        self._tree.commit()

    def get(self, key):
        self._assert_not_closed()
        return self._tree.get(key)

    def set(self, key, value):
        self._assert_not_closed()
        return self._tree.set(key, value)

    def getRootKey(self):
        return self._tree.rootkey()

    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)

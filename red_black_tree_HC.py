from immutable_tree import *


class Color(object):
    RED = 0
    BLACK = 1

class RedBlackNodeRef(ValueRef):
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
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
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

    def __init__(self, left_ref, key, value_ref, right_ref, color):
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref
        self.color = color

    def blacken(self):
        if self.is_red():
            self.color = Color.BLACK

    def is_black(self):
        return self.color == Color.BLACK

    def is_red(self):
        return self.color == Color.RED


class RedBlackTree(BinaryTree):

    # def __init__(self, left_ref, key, value_ref, right_ref, color=Color.RED):
    #     self.key = key
    #     self.value_ref = value_ref
    #     self.right_ref = right_ref
    #     self.value_ref = value_ref
    #     self.color = color

    def _refresh_tree_ref(self):
        "get reference to new tree if it has changed"
        self._tree_ref = RedBlackRef(
            address=self._storage.get_root_address())

    def is_empty(self):
        return False

    def _blacken(self):
        self._follow(self._tree_ref)._blacken()

    def rotate_left(self):
        # self.right = EmptyRedBlackTree().update(self.right.left)
        # return RedBlackTree(
        #     RedBlackTree(
        #         self.left,
        #         self.value,
        #         EmptyRedBlackTree().update(self.right.left),
        #         color=self.color,
        #     ),
        #     self.right.value,
        #     self.right.right,
        #     color=self.right.color,
        # )

        node = self._follow(self._tree_ref)
        left = self._follow(node.left_ref)
        right = self._follow(node.right_ref)
        node.left_ref = node.value_ref
        node.right_ref = right.right_ref
        node.value_ref = right.value_ref
        self.color = right.color


    def rotate_right(self):
        # return RedBlackTree(
        #     self.left.left,
        #     self.left.value,
        #     RedBlackTree(
        #         EmptyRedBlackTree().update(self.left.right),
        #         self.value,
        #         self.right,
        #         color=self.color,
        #     ),
        #     color=self.left.color,
        # )

        node = self._follow(self._tree_ref)
        left = self._follow(node.left_ref)
        right = self._follow(node.right_ref)
        node.right_ref = node.value_ref
        node.value_ref = left.value_ref
        node.left_ref = left.left_ref
        self.color = left.color


    def recolored(self):
        node = self._follow(self._tree_ref)
        left = self._follow(node.left_ref)
        right = self._follow(node.right_ref)
        left._blacken()
        right._blacken()
        node.color = Color.RED

    def balance(self):
        if self.is_red():
            return self

        if self.left.is_red():
            if self.right.is_red():
                return self.recolored()
            if self.left.left.is_red():
                return self.rotate_right().recolored()
            if self.left.right.is_red():
                return RedBlackTree(
                    self.left.rotate_left(),
                    self.value,
                    self.right,
                    color=self.color,
                ).rotate_right().recolored()
            return self

        if self.right.is_red():
            if self.right.right.is_red():
                return self.rotate_left().recolored()
            if self.right.left.is_red():
                return RedBlackTree(
                    self.left,
                    self.value,
                    self.right.rotate_right(),
                    color=self.color,
                ).rotate_left().recolored()
        return self

    def update(self, node):
        if node.is_empty():
            return self
        if node.value < self.value:
            return RedBlackTree(
                self.left.update(node).balance(),
                self.value,
                self.right,
                color=self.color,
            ).balance()
        return RedBlackTree(
            self.left,
            self.value,
            self.right.update(node).balance(),
            color=self.color,
        ).balance()

    # def insert(self, key, value):
    #     return self.update(
    #         RedBlackTree(
    #             EmptyRedBlackTree(),
    #             value,
    #             EmptyRedBlackTree(),
    #             color=Color.RED,
    #         )
    #     ).blacken()

    def set(self, key, value, color):
        "set a new value in the tree. will cause a new tree"
        #try to lock the tree. If we succeed make sure
        #we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        #get current top-level node and make a value-ref
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        #insert and get new tree ref
        self._tree_ref = self._insert(node, key, value_ref, color)


    def _insert(self, node, key, value_ref, color=Color.RED):
        "insert a new node creating a new path from root"
        #create a tree if there was none so far
        if node is None:
            new_node = RedBlackNode(
                RedBlackNodeRef(), key, value_ref, RedBlackNodeRef(), color)
        elif key < node.key:
            new_node = RedBlackNode.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref, color).balance())
        elif key > node.key:
            new_node = RedBlackNode.from_node(
                node,
                right_ref=self._insert(
                    self._follow(node.right_ref), key, value_ref, color).balance())
        else: #create a new node to represent this data
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return RedBlackNodeRef(referent=new_node)


class EmptyRedBlackTree(RedBlackTree):

    def __init__(self):
        self._color = Color.BLACK

    def is_empty(self):
        return True

    def insert(self, value):
        return RedBlackTree(
            EmptyRedBlackTree(),
            value,
            EmptyRedBlackTree(),
            color=Color.RED,
        )

    def update(self, node):
        return node

    @property
    def left(self):
        return EmptyRedBlackTree()

    @property
    def right(self):
        return EmptyRedBlackTree()

    def __len__(self):
        return 0

class DBDB(object):

    def __init__(self, f):
        self._storage = Storage(f)
        self._tree = BinaryTree(self._storage)

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
        return self._tree.set(key, value, color=Color.RED)

    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)

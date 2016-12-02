import os
import struct
import portalocker
import pickle

class ValueRef(object):
    """
    This class produces a reference to a string value on the disk.   
    """

    def __init__(self, referent=None, address=0):
        """
        The constructor of the class takes for arguments a referent and address
        
        Parameters
        ----------
        
        referent: value to store for the string, optional
        address: target address for the string value, optional
        
        Attributes
        ----------
        
        self._referent: value
        self._address: address
        """
        self._referent = referent #value to store
        self._address = address #address to store at
        
    @property
    def address(self):
        """
        Method that returns the address stored in ValueRef.
        
        """
        return self._address
    
    def prepare_to_store(self, storage):
        """
        Method that passes in preparation for storage
        
        Parameter
        ---------
        
        storage: a storage address at which the value is stored
        
        """
        pass

    @staticmethod
    def referent_to_bytes(referent):
        """
        Method that encodes the referent in utf-8
        
        Parameter
        ---------
        
        referent: the value to be stored in the class
        
        """
        return referent.encode('utf-8')

    @staticmethod
    def bytes_to_referent(bytes):
        """
        Method that decodes the stored bytes in utf-8
        
        Parameter
        ---------
        
        bytes: the storage encoded in utf-8
        
        """
        return bytes.decode('utf-8')

    
    def get(self, storage):
        """
        Method that reads bytes for the value from the disk.
        
        Parameter
        ---------
        
        storage: the referent's storage address, to be decoded and then obtained through self._referent.
        
        """
        "read bytes for value from disk"
        if self._referent is None and self._address:
            self._referent = self.bytes_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        """
        Method that stores bytes for the value to the disk.
        
        Parameter
        ---------
        
        storage: the referent's storage address, to be encoded and then stored in self._address,
        
        """
        #called by BinaryNode.store_refs
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage)
            self._address = storage.write(self.referent_to_bytes(self._referent))

class BinaryNodeRef(ValueRef):
    """
    This class produces a reference to a binary search tree node on the disk.   
    """
    
    #calls the BinaryNode's store_refs
    def prepare_to_store(self, storage):
        """
        Method that stores refs for the node 
        
        Parameter
        ---------
        
        storage: a storage address at which the value is stored
        
        """
        if self._referent:
            self._referent.store_refs(storage)

    @staticmethod
    def referent_to_bytes(referent):
        """
        Method that uses pickle to convert the node to bytes
        
        Parameter
        ---------
        
        referent: the value to be stored in the node
        
        """
        return pickle.dumps({
            'left': referent.left_ref.address,
            'key': referent.key,
            'value': referent.value_ref.address,
            'right': referent.right_ref.address,
        })

    @staticmethod
    def bytes_to_referent(string):
        """
        Method that unpickles bytes to obtain a node object
        
        Parameter
        ---------
        
        referent: the value to be stored in the node
        
        """
        d = pickle.loads(string)
        return BinaryNode(
            BinaryNodeRef(address=d['left']),
            d['key'],
            ValueRef(address=d['value']),
            BinaryNodeRef(address=d['right']),
        )
              
class BinaryNode(object):
    """
    This class stores data associated with a particular node whose refs are stored in BinaryNodeRef
    """
    @classmethod
    def from_node(cls, node, **kwargs):
        """
        Method that clones a node given changes from another node
    
        Parameters
        ----------
    
        node: the node whose properties will be emulated
        kwargs: obtain key, value, right and left refs to clone
    
        """
        return cls(
            left_ref=kwargs.get('left_ref', node.left_ref),
            key=kwargs.get('key', node.key),
            value_ref=kwargs.get('value_ref', node.value_ref),
            right_ref=kwargs.get('right_ref', node.right_ref),
        )

    def __init__(self, left_ref, key, value_ref, right_ref):
        """
        The constructor of the class takes for arguments the refs belonging to the node itself, its right child, its left child, and its key.
    
        Parameters
        ----------
    
        left_ref: reference for left node, mandatory
        key: the key value of the node, mandatory
        value_ref: reference for node, mandatory
        right_ref: reference for right node, mandatory
        
        Attributes
        ----------
    
        self.left_ref: ref address
        self.key: value
        self.value_ref: ref address
        self.right_ref: ref address
        
        """
        self.left_ref = left_ref
        self.key = key
        self.value_ref = value_ref
        self.right_ref = right_ref

    def store_refs(self, storage):
        """
        Method that stores all of the node's properties in references
    
        Parameters
        ----------
    
        storage: the storage at which to store refs
    
        """
        self.value_ref.store(storage)
        #calls BinaryNodeRef.store. which calls
        #BinaryNodeRef.prepate_to_store
        #which calls this again and recursively stores
        #the whole tree
        self.left_ref.store(storage)
        self.right_ref.store(storage)
        
        
class BinaryTree(object):
    """
    Immutable Binary Tree class. Constructs new tree on changes.
    """
    
    def __init__(self, storage):
        """
        The constructor of the class takes for arguments a storage reference
        
        Parameters
        ----------
        
        storage: storage reference address, compulsory
        
        Attributes
        ----------
        
        self._storage: address
        self._refresh_tree_ref(): address
        """
        self._storage = storage
        self._refresh_tree_ref()

    def commit(self):
        """
        Method to ensure that changes are final only when committed
        
        """
        
        #triggers BinaryNodeRef.store
        self._tree_ref.store(self._storage)
        #make sure address of new tree is stored
        self._storage.commit_root_address(self._tree_ref.address)

    def _refresh_tree_ref(self):
        """
        Method to get reference to new tree if it has changed
        
        """
        
        self._tree_ref = BinaryNodeRef(
            address=self._storage.get_root_address())

    def get(self, key):
        """
        Method that obtains the value stores in a given key
        
        Parameter
        ---------
        
        key: a lookup value that will throw a KeyError if it doesn't exist in the tree
        
        """
        
        #if tree is not locked by another writer
        #refresh the references and get new tree if needed
        if not self._storage.locked:
            self._refresh_tree_ref()
        #get the top level node
        node = self._follow(self._tree_ref)
        #traverse until you find appropriate node
        while node is not None:
            if key < node.key:
                node = self._follow(node.left_ref)
            elif key > node.key:
                node = self._follow(node.right_ref)
            else:
                return self._follow(node.value_ref)
        raise KeyError

    def set(self, key, value):
        """
        Method that sets a new value in the tree. Since the tree is immutable, a new tree is created.
        
        Parameters
        ----------
        
        key: a lookup value
        value: the value that will be stored for the key
        
        """
        
        #try to lock the tree. If we succeed make sure
        #we dont lose updates from any other process
        if self._storage.lock():
            self._refresh_tree_ref()
        #get current top-level node and make a value-ref
        node = self._follow(self._tree_ref)
        value_ref = ValueRef(value)
        #insert and get new tree ref
        self._tree_ref = self._insert(node, key, value_ref)


    def _insert(self, node, key, value_ref):
        """
        Method that inserts a new node, creating a new path from tree's root.
        
        Parameters
        ----------
        
        key: a lookup value
        node: address
        value_ref: the reference address of the new node as per its new path from the tree root
        
        """
        #create a tree if there was none so far
        if node is None:
            new_node = BinaryNode(
                BinaryNodeRef(), key, value_ref, BinaryNodeRef())
        elif key < node.key:
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._insert(
                    self._follow(node.left_ref), key, value_ref))
        elif key > node.key:
            new_node = BinaryNode.from_node(
                node,
                right_ref=self._insert(
                    self._follow(node.right_ref), key, value_ref))
        else: #create a new node to represent this data
            new_node = BinaryNode.from_node(node, value_ref=value_ref)
        return BinaryNodeRef(referent=new_node)

    def delete(self, key):
        """
        Method that deletes node given key value, creating both a new tree and path to any nodes connected to the deleted node.
        
        Parameters
        ----------
        
        key: a lookup value
        
        """
    
        if self._storage.lock():
            self._refresh_tree_ref()
        node = self._follow(self._tree_ref)
        self._tree_ref = self._delete(node, key)

    def _delete(self, node, key):
        """
        Method that implements the deletion of a node.
        
        Parameters
        ----------
        
        node: reference address for deleted node
        key: a lookup value
        
        """
        
        if node is None:
            raise KeyError
        elif key < node.key:
            new_node = BinaryNode.from_node(
                node,
                left_ref=self._delete(
                    self._follow(node.left_ref), key))
        elif key > node.key:
            new_node = BinaryNode.from_node(
                node,
                right_ref=self._delete(
                    self._follow(node.right_ref), key))
        else:
            left = self._follow(node.left_ref)
            right = self._follow(node.right_ref)
            if left and right:
                replacement = self._find_max(left)
                left_ref = self._delete(
                    self._follow(node.left_ref), replacement.key)
                new_node = BinaryNode(
                    left_ref,
                    replacement.key,
                    replacement.value_ref,
                    node.right_ref,
                )
            elif left:
                return node.left_ref
            else:
                return node.right_ref
        return BinaryNodeRef(referent=new_node)

    def _follow(self, ref):
        """
        Method that identifies a node from a reference address.
        
        Parameters
        ----------
        
        ref: reference address for a particular node
        
        """        
        
        #calls BinaryNodeRef.get
        return ref.get(self._storage)

    def _find_max(self, node):
        """
        Method that finds the right-most node associated with a particular node,
        If it doesn't exist, the input node itself is returned.
        
        Parameters
        ----------
        
        node: the node for which we would like to find any max leaf
        
        """
        while True:
            next_node = self._follow(node.right_ref)
            if next_node is None:
                return node
            node = next_node

class Storage(object):
    SUPERBLOCK_SIZE = 4096
    INTEGER_FORMAT = "!Q"
    INTEGER_LENGTH = 8

    def __init__(self, f):
        self._f = f
        self.locked = False
        #we ensure that we start in a sector boundary
        self._ensure_superblock()

    def _ensure_superblock(self):
        "guarantee that the next write will start on a sector boundary"
        self.lock()
        self._seek_end()
        end_address = self._f.tell()
        if end_address < self.SUPERBLOCK_SIZE:
            self._f.write(b'\x00' * (self.SUPERBLOCK_SIZE - end_address))
        self.unlock()

    def lock(self):
        "if not locked, lock the file for writing"
        if not self.locked:
            portalocker.lock(self._f, portalocker.LOCK_EX)
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        if self.locked:
            self._f.flush()
            portalocker.unlock(self._f)
            self.locked = False

    def _seek_end(self):
        self._f.seek(0, os.SEEK_END)

    def _seek_superblock(self):
        "go to beginning of file which is on sec boundary"
        self._f.seek(0)

    def _bytes_to_integer(self, integer_bytes):
        return struct.unpack(self.INTEGER_FORMAT, integer_bytes)[0]

    def _integer_to_bytes(self, integer):
        return struct.pack(self.INTEGER_FORMAT, integer)

    def _read_integer(self):
        return self._bytes_to_integer(self._f.read(self.INTEGER_LENGTH))

    def _write_integer(self, integer):
        self.lock()
        self._f.write(self._integer_to_bytes(integer))

    def write(self, data):
        "write data to disk, returning the adress at which you wrote it"
        #first lock, get to end, get address to return, write size
        #write data, unlock <==WRONG, dont want to unlock here
        #your code here
        self.lock()
        self._seek_end()
        object_address = self._f.tell()
        self._write_integer(len(data))
        self._f.write(data)
        return object_address

    def read(self, address):
        self._f.seek(address)
        length = self._read_integer()
        data = self._f.read(length)
        return data

    def commit_root_address(self, root_address):
        self.lock()
        self._f.flush()
        #make sure you write root address at position 0
        self._seek_superblock()
        #write is atomic because we store the address on a sector boundary.
        self._write_integer(root_address)
        self._f.flush()
        self.unlock()

    def get_root_address(self):
        #read the first integer in the file
        #your code here
        self._seek_superblock()
        root_address = self._read_integer()
        return root_address

    def close(self):
        self.unlock()
        self._f.close()

    @property
    def closed(self):
        return self._f.closed
        
class it_DBDB(object):

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
        return self._tree.set(key, value)

    def delete(self, key):
        self._assert_not_closed()
        return self._tree.delete(key)

def it_connect(dbname):
    try:
        f = open(dbname, 'r+b')
    except IOError:
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return it_DBDB(f)

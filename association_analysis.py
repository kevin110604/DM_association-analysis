import pandas as pd
import itertools

class HeaderTableNode:
    def __init__(self):
        self.head = None
        self.tail = None

class FPtreeNode:
    def __init__(self, val, parent=None):
        self.val = val
        self.count = 1
        self.parent = parent
        self.children = []
        self.next = None
    def insert_frequent_items(self, items, hdtable):
        # If there is no frequent item
        if len(items) == 0:
            return
        item = items[0]
        for child in self.children:
            if child.val == item:
                child.count += 1
                child.insert_frequent_items(items[1:], hdtable)
                return
        # If cannot find the item among children
        new_child = FPtreeNode(item, self)
        # Add new node to header table
        if hdtable[item].head == None:
            hdtable[item].head = new_child
            hdtable[item].tail = new_child
        else:
            hdtable[item].tail.next = new_child
            hdtable[item].tail = new_child
        # Add new node to current node's children
        self.children.append(new_child)
        new_child.insert_frequent_items(items[1:], hdtable)

class CondPatternBase:
    def __init__(self, pattern, freq):
        self.pattern = pattern
        self.freq = freq

class FreqPattern:
    def __init__(self, pattern, support):
        self.pattern = pattern
        self.support = support

# Load data
df = pd.read_csv('data_1_3_20_10_5.csv')
# df = pd.read_csv('fcam.csv')
# Candidate 1-itemset
C1 = df['Item'].value_counts()
# Frequent 1-itemset
minsup = 3
minconf = 0.8
L1 = C1.loc[C1.values >= minsup]

# Init dictionary for every transaction
trans_num = df['TransID'].max()
di = {}
for i in range(1, trans_num + 1):
    di[i] = []
# Extract info from df to dictionary
df_num = len(df)
for i in range(df_num):
    index = df.iloc[i][0]
    item = df.iloc[i][2]    
    di[index] += [item]

one_fp = L1.index.values.tolist()
# print(one_fp)

# Init dictionary for ordered frequent items of every transaction
ofi = {}
for i in range(1, trans_num + 1):
    ofi[i] = []
# Construct ordered frequent items of every transaction
for i in range(1, trans_num + 1):
    for item in one_fp:
        if item in di[i]:
            ofi[i] += [item]

# Init header table
HeaderTable = {}
for item in one_fp:
    new_node = HeaderTableNode()
    HeaderTable[item] = new_node

# Construct FP-tree
FPtree = FPtreeNode('root')
for i in range(1, trans_num + 1):
    FPtree.insert_frequent_items(ofi[i], HeaderTable)

# Generate conditional pattern base
CondBase = {}
for item in one_fp:
    # Init
    CondBase[item] = []
    # Start from head, and no need to traverse the leaf node
    listnode = HeaderTable[item].head
    treenode = listnode.parent
    # Traversal of linked-list
    while True:
        pattern = []
        # Traversal of tree
        while True:
            if treenode.val == 'root':
                # print()
                break
            # print('%s ' % treenode.val, end = '')
            pattern.insert(0, treenode.val)
            treenode = treenode.parent
        # Create a new base for this item
        if len(pattern) > 0:
            new_base = CondPatternBase(pattern, listnode.count)
            CondBase[item].append(new_base)
            # print('item = %s, count = %d: ' % (item, listnode.count), end = '\t')
            # print(pattern)
        # Reach the end of the list of this item
        if listnode.next == None:
            break
        # Continue to next node in the list, and no need to traverse the leaf node
        listnode = listnode.next
        treenode = listnode.parent

# Accumulate the count for each item in the base
freq = {}
for item1 in one_fp:
    freq[item1] = {}
    for item2 in one_fp:
        freq[item1][item2] = 0
    for base in CondBase[item1]:
        for item3 in base.pattern:
            freq[item1][item3] += base.freq    
    # print(item1)
    # print(freq[item1])
# (conditional FP-tree)
condFPtree = {}
for item1 in one_fp:
    tmp_pattern = []
    for item2 in one_fp:
        if freq[item1][item2] >= minsup:
            tmp_pattern.append(item2)
    if len(tmp_pattern) > 0:
        condFPtree[item1] = tmp_pattern
# print(condFPtree)

# Generate frequent patterns
FreqPat = []
for key in condFPtree:
    x = condFPtree[key]
    for L in range(1, len(x)+1):
        for subset in itertools.combinations(x, L):
            pat = list(subset)
            pat.append(key)
            FreqPat.append(pat)
print(FreqPat)

# Rule generation
# for each frequent itemset m do 
#     for each subset p of m do
#         if (support(m)/support(p)) >= min_confidence then 
#             output the rule p->(m-p)


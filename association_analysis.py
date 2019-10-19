import pandas as pd

# Load data
df = pd.read_csv('data_1_3_20_10_5.csv')
# Candidate 1-itemset
C1 = df['Item'].value_counts()
# Frequent 1-itemset
minsup = 80
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
print(one_fp)

# Init dictionary for ordered frequent items of every transaction
ofi = {}
for i in range(1, trans_num + 1):
    ofi[i] = []
# Construct ordered frequent items of every transaction
for i in range(1, trans_num + 1):
    for item in one_fp:
        if item in di[i]:
            ofi[i] += [item]

class FPtreeNode:
    def __init__(self, val, parent=None):
        self.val = val
        self.count = 0
        self.parent = parent
        self.children = []
    def insert_frequent_items(self, items):
        # If there is no frequent item
        if len(items) == 0:
            return
        item = items[0]
        for child in self.children:
            if child.val == item:
                child.count += 1
                child.insert_frequent_items(items[1:])
                return
        # If cannot find the item among children
        new_child = FPtreeNode(item, self)
        self.children.append(new_child)
        new_child.insert_frequent_items(items[1:])

# Construct FP-tree
FPtree = FPtreeNode('root')
for i in range(1, trans_num + 1):
    FPtree.insert_frequent_items(ofi[i])

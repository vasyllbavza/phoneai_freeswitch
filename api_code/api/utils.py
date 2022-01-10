class TreeNode(dict):
    def __init__(self, data, children=None):
        super().__init__()
        self.__dict__ = self
        self.data = data
        # self.child = []
        self.children = list(children) if children is not None else []

    def insert(self, obj):
        self.child.append(obj)


    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = Tree(dict_['name'], dict_['children'])
#        node.children = [TreeNode.from_dict(child) for child in node.children]
        node.children = list(map(Tree.from_dict, node.children))
        return node

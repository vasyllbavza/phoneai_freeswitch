class TreeNode(dict):

    def __init__(self, id, menu, children=None, key = None, parent_text = None, keys_to_reach = None):
        super().__init__()
        self.__dict__ = self
        self.id = id
        self.info = {
            "parent_text": parent_text,
            "keys_to_reach": keys_to_reach
        }
        self.key = key
        self.audio_text = menu["audio_text"]
        self.children = list(children) if children is not None else []

    def insert(self, obj):
        self.child.append(obj)


    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = TreeNode(dict_['name'], dict_['key'], dict_['children'])
#        node.children = [TreeNode.from_dict(child) for child in node.children]
        node.children = list(map(TreeNode.from_dict, node.children))
        return node

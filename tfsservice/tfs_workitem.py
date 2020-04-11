from tfs import TFSAPI
from collections import defaultdict

class TfsWorkitem:
    '''TFS Workitem class (Incapsulated TFSAPI Workitem)
    Access to propertiest with indexer [] method
    '''

    def __init__(self, workitem):
        self.__wi = workitem

        self.__id = workitem.id
        self.__title = workitem['Title']
        self.__item_type = workitem['WorkItemType']

        self.__parent_id = workitem.parent.id if workitem.parent else None

        return

    def __repr__(self):
        return str('%s %s %s' % (self.__item_type, self.__id, self.__title))

    @property
    def id(self):
        return self.__id

    @property
    def title(self):
        return self.__title
    
    @property
    def item_type(self):
        return self.__item_type

    @property
    def parent_id(self):
        return self.__parent_id
    
    @property
    def item_url(self):
        return self.__wi.url

    def __getitem__(self, key):
        return self.__wi[key]

    def __setitem__(self, key, value):
        self.__wi[key] = value

    def get_child_ids(self):
        '''Get child items ids (Hierarchy-Forward)

        Returns:
            ids (list(int)): list of child ids
        '''

        wi_len_str = len('workItems/')

        def extract_id_from_url(url):
            id = str('0')
            wi_substr = url.find('workItems/')
            
            if wi_substr > 1:
                start = int(wi_substr + wi_len_str)
                id = url[start:]
            
            return int(id)

        childs = self.__wi.find_in_relation('Hierarchy-Forward')

        if childs:
            res = [extract_id_from_url(child['url']) for child in childs]
            return res
        else:
            return None

    def get_affect_ids(self):
        '''Get affect items ids (Affects-Forward)

        Returns:
            ids (list(int)): list of child ids
        '''

        wi_len_str = len('workItems/')

        def extract_id_from_url(url):
            id = str('0')
            wi_substr = url.find('workItems/')
            
            if wi_substr > 1:
                start = int(wi_substr + wi_len_str)
                id = url[start:]
            
            return int(id)

        affects = self.__wi.find_in_relation('Affects-Forward')

        if affects:
            res = [extract_id_from_url(child['url']) for child in affects]
            return res
        else:
            return None

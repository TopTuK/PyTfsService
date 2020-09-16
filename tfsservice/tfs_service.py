from tfs import TFSAPI
from requests_ntlm import HttpNtlmAuth
from tfs_workitem import TfsWorkitem

'''
TFAPI: https://devopshq.github.io/tfs/api.html
Packaging: https://python-packaging.readthedocs.io/en/latest/
'''

class TfsService:
    """
    TFS Service class
    """

    def __init__(self, tfs_server, tfs_project='DefaultCollection'):
        self.__tfs_server = tfs_server
        self.__tfs_project = tfs_project

        self.__is_connected = False
        self.__tfs_client = None
        
        return

    @property 
    def is_connected(self):
        return self.__is_connected

    def connect(self, user_name, user_password, connection_test_item_id):
        '''Connect to TFS Service function
        Using HttpNtlmAuth authication

        Parameters:
            user_name (str): user name
            user_password (str): user password
            connection_test_item_id (int): id of test workitem for connection test
        
        Returns:
            is_connected (Boolean): True if successfully connected. False owerwise.
        '''
        self.__tfs_client = TFSAPI(self.__tfs_server, project=self.__tfs_project,
            user=user_name, password=user_password, auth_type=HttpNtlmAuth)
        
        try:
            wi = self.__tfs_client.get_workitem(int(connection_test_item_id))
            self.__is_connected = True if wi else False
        except:
            self.__is_connected = False

        return self.__is_connected
    
    def get_workitem(self, item_id):
        '''Get workitem and load properties

        Parameters:
            item_id (int): workitem id

        Returns:
            workitem (TfsWorkitem): Workitem with properties. None owerwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        wi = self.__tfs_client.get_workitem(item_id)
        if wi:
            return TfsWorkitem(wi)
        else:
            return None
        
    def get_workitems(self, item_ids):
        '''Get workitems and load properties

        Parameters:
            item_ids (list of int): workitem ids list

        Returns:
            workitems (list of TfsWorkitem): List of workitems with properties. None owerwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if not isinstance(item_ids, list):
            raise NameError('item_ids should be list')

        ids = [int(id) for id in item_ids]
        workitems = self.__tfs_client.get_workitems(ids)

        if workitems:
            res = [TfsWorkitem(wi) for wi in workitems]
            return res
        else:
            return None

    def save_raw_workitem(self, item_id, props):
        '''Save workitem with given properties

        Parameters:
            item_id (int): workitem id
            props (dict(str, str)): dictionary of properties
        
        Returns:
            result (Boolean): True if saved, False owerwise
        '''
        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if not isinstance(props, dict):
            raise NameError('props should be dictonary')

        wi = self.__tfs_client.get_workitem(int(item_id))
        if wi:
            for prop_name, prop_value in props.items():
                wi[prop_name] = prop_value

            return True
        else:
            return False
    
    def create_workitem(self, workitem_type, required_fields, props=None):
        '''Create new tfs workitem with given type

        Parameters:
            workitem_type (str): workitem type
            required_fields (dict(str, str)): Required. Dictonary of setted fields.
            props (dict(str, str)): additional dictionary of properties which will be setted after creating item
        
        Returns:
            workitem (TfsWorkitem): Workitem with properties. None overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if (required_fields != None) and (not isinstance(required_fields, dict)):
            raise NameError('required_fields should be dictonary')

        if (props != None) and (not isinstance(props, dict)):
            raise NameError('props should be dictonary')

        workitem = self.__tfs_client.create_workitem(workitem_type, fields=required_fields)
        if workitem:
            wi = TfsWorkitem(workitem)
            
            if props != None:
                for prop_name, prop_value in props.items():
                    wi[prop_name] = prop_value
            
            return wi
        else:
            return None

    def copy_workitem(self, 
        workitem, with_links_and_attachments=True,
        suppress_notifications=True, props=None):
        '''Create copy of tfs workitem and set properties

        Parameters:
            workitem (TfsWorkitem or int): workitem or workitem ID
            with_links_and_attachments (Boolean): create copy with links and attachments
            suppress_notifications (Boolean): suppress notifications
            props (dict(str, str)): dictionary of properties
        
        Returns:
            workitem (TfsWorkitem): Copy of given Workitem with properties. None overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if (props != None) and (not isinstance(props, dict)):
            raise NameError('props should be dictonary')

        id = workitem.id if workitem is TfsWorkitem else workitem
        source_wi = self.__tfs_client.get_workitem(id)
        if source_wi:
            copy_wi = self.__tfs_client.copy_workitem(source_wi, 
                with_links_and_attachments=with_links_and_attachments,
                suppress_notifications=suppress_notifications)
            
            if copy_wi:
                wi = TfsWorkitem(copy_wi)
                
                if props != None:
                    for prop_name, prop_value in props.items():
                        wi[prop_name] = prop_value
                
                return wi
            else:
                return None
        else:
            raise NameError('Source workitem is None')
    
    def run_query(self, query):
        '''Runs tfs query and return list of workitems

        Parameters:
            query (str): Query string. Named query in folder or query GUID
        
        Returns:
            workitem (list of TfsWorkitem): List of workitems. None overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        query = self.__tfs_client.run_query(query)
        if query:
            workitems = [TfsWorkitem(wi) for wi in query.workitems] # Lazy generator
            
            return workitems
        else:
            return None

    # uri_params: https://docs.microsoft.com/en-us/rest/api/azure/devops/wit/Wiql/Query%2520By%2520Wiql?view=azure-devops-rest-5.0&viewFallbackFrom=vsts-rest-4.1#uri-parameters
    def run_wiql(self, wiql, uri_params=None):
        '''Runs tfs wiql and return list of workitems

        Parameters:
            wiql (str): wiql query string.
            uri_params (dict (str, str)): extra URI parameters as a dictionary (only works for parameters that come at the end of the link)
        
        Returns:
            workitem (list of TfsWorkitem): List of workitems. None overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if (uri_params != None) and (not isinstance(uri_params, dict)):
            raise NameError('URI params should be dictonary. Search \'Wiql - Query By Wiql\' URI Parameters web page')

        query = self.__tfs_client.run_wiql(wiql) if uri_params == None else self.__tfs_client.run_wiql(wiql, params=uri_params)
        if query:
            workitems = [TfsWorkitem(wi) for wi in query.workitems] # Lazy generator
            
            return workitems
        else:
            return None

    #### https://devopshq.github.io/tfs/advanced.html ####
    ##### https://docs.microsoft.com/ru-ru/rest/api/azure/devops/wit/?view=azure-devops-rest-5.0 ######

    # System.LinkTypes.Hierarchy-Reverse
    def add_parent_link(self, source_workitem, dest_workitem):
        '''Add parent link from source workitem to destination workitem

        Parameters:
            source_workitem (TfsWorkitem): Source workitem
            dest_workitem (TfsWorkitem): Destination workitem
        
        Returns:
            Result (Boolean): True if parent link was added, False overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')
        
        if source_workitem.add_parent_link(dest_workitem):
            return True
        else:
            return False

    # System.LinkTypes.Hierarchy-Forward
    def add_child_link(self, source_workitem, dest_workitem):
        '''Add child link from source workitem to destination workitem

        Parameters:
            source_workitem (TfsWorkitem): Source workitem
            dest_workitem (TfsWorkitem): Destination workitem
        
        Returns:
            Result (Boolean): True if child link was added, False overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if source_workitem.add_child_link(dest_workitem):
            return True
        else:
            return False

    # Microsoft.VSTS.Common.Affects-Forward
    def add_affect_link(self, source_workitem, dest_workitem):
        '''Add affects link from source workitem to destination workitem

        Parameters:
            source_workitem (TfsWorkitem): Source workitem
            dest_workitem (TfsWorkitem): Destination workitem
        
        Returns:
            Result (Boolean): True if affects link was added, False overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if source_workitem.add_affect_link(dest_workitem):
            return True
        else:
            return False

    # Microsoft.VSTS.Common.Affects-Reverse
    def add_affected_by_link(self, source_workitem, dest_workitem):
        '''Add affected by link from source workitem to destination workitem

        Parameters:
            source_workitem (TfsWorkitem): Source workitem
            dest_workitem (TfsWorkitem): Destination workitem
        
        Returns:
            Result (Boolean): True if affected by link was added, False overwise
        '''

        if not self.__is_connected:
            raise NameError('Disconnected from TFS Service')

        if source_workitem.add_affected_by_link(dest_workitem):
            return True
        else:
            return False

    
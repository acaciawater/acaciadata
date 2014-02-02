class Generator(object):

    def __init__(self, *args, **kwargs):
        pass

    def get_header(self,fil):
        return {}

    def get_data(self,fil,**kwargs):
        return []
        
    def get_default_args(self):
        return {}
        
    def upload(self,fil,**kwargs):
        pass
    
    def get_parameters(self,fil):
        ''' return list of all parameters in the datafile '''
        return []
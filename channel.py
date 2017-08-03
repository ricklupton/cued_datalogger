import numpy as np
'''
The idea of this class is that users will only need to interact with
the ChannelSet class to interact with the rest of the class
'''

class ChannelSet():
    """The class for storing a set of channels in"""
    def __init__(self, channels=None):
        self.chans = np.empty(0, dtype=Channel)
        
        if channels:
            for i in range(channels):
                self.add_channel(i)
                
                
    # Add a Channel
    # TODO: allow inputs of a Channel class
    def add_channel(self,cid):
        self.chans = np.append(self.chans, Channel(cid))
    
    # Add a DataSet to a Channel
    # TODO: allow multichannel adding
    # TODO: Auto create the DataSet with the input being the id    
    def chan_add_dataset(self,num,datasets):
        self.chans[num].add_dataset(datasets)
    
    # Set the data of a DataSet in a Channel
    # TODO: allow multidata setting   
    def chan_set_data(self,num,id_,datasets):
        self.chans[num].set_data(id_,datasets)
    
    # Get the metadatas of specified Channels
    def get_metadatas(self,chan_nums,meta_names): 
        metadatas = {}
        if type(chan_nums) == int:
            chan_nums = [chan_nums]
        
        if type(meta_names) == str:
            meta_names = [meta_names]
            
        for n in chan_nums:
            mdata = {}
            for m in meta_names:
                try:
                    mdata[m.lower()] = self.chans[n].get_metadata(m.lower())
                except IndexError:
                    print('The specified channel cannot be found')
            metadatas[str(n)] = mdata
        
        return metadatas
    
    # Get the metadatas of specified Channels
    def set_metadatas(self,chan_nums,meta_dict):
        if not type(meta_dict) == dict:
            raise Exception('Please Enter a Dictionary type')
            
        if type(chan_nums) == int:
            chan_nums = [chan_nums]
        else:    
            chan_nums = list(set(chan_nums))
            chan_nums.sort()
        
        for n in chan_nums:
            try:
                self.chans[n]
            except IndexError:
                print('The specified channel cannot be found')
                break
            for m,v in zip(iter(meta_dict.keys()),iter(meta_dict.values())):
                    self.chans[n].set_metadata(m.lower(),v)
                
                
    def __len__(self):
        return(len(self.chans))
    
class Channel():
    """The class for storing a channel in"""
    def __init__(self,cid,name=None,
                 datasets=None,values=None,id_=None):
        
        # Put metadata here
        self.cid = int(cid)
        self.name = name
        self.cal_factor = 1
        self.units = 'm/s'
        self.tags = []
        self.comments = ''
        
        # Put data here
        self.datasets = np.empty((0), dtype=DataSet)
        if datasets is not None:
            for dataset in datasets:
                self.add_dataset(dataset)
        
        if values:
            self.add_dataset(DataSet(id_, values))
    
    def available_datasets(self):
        return [ds.id_ for ds in self.datasets]
    
    def is_dataset(self,id_):
        return any([ds.id_ == id_ for ds in self.datasets])
    
    def add_dataset(self, id_ ,values=None):
        if not self.is_dataset(id_):
            self.datasets = np.append(self.datasets, DataSet(id_,values))
        else:
            raise Exception('You already have that dataset!')
            
    def set_data(self, id_, values):
        for ds in self.datasets:
            if ds.id_ == id_:
                ds.set_values(values)
                break
            else:
                raise Exception('No such dataset!')
                
    def data(self, id_):
        for ds in self.datasets:
            if ds.id_ == id_:
                return ds.values
            else:
                raise Exception('No such dataset!')
    
    def get_metadata(self,meta_name):
        mdata = None
        if hasattr(self,meta_name):
            mdata = getattr(self,meta_name)
        else:
            raise Exception('No such attribute')
            
        return mdata
    
    def set_metadata(self,meta_name,val):
        if hasattr(self,meta_name):
                setattr(self,meta_name,val)
    

class DataSet():
    """The class for storing data in"""
    def __init__(self,id_,values=None):
        self.id_ = str(id_)
        self.values = np.asarray(values)
    
    def set_id_(self, id_):
        self.id_ = str(id_)
    
    def set_values(self, values):
        self.values = np.asarray(values)
        
        

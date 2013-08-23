import os.path
import re, itertools, uuid
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured
from io import RawIOBase, BufferedRWPair, BufferedWriter

#keep consistent path separators
pathjoin = lambda *args: os.path.join(*args).replace("\\", "/")

try:
    import azure
    import azure.storage
except ImportError:
    raise ImproperlyConfigured(
        "Could not load Azure bindings. "
        "See https://github.com/WindowsAzure/azure-sdk-for-python")

from storages.utils import setting


def clean_name(name):
    return os.path.normpath(name).replace("\\", "/")


class AzureStorage(Storage):
    chunk_size = 65536 # Those were the days

    def __init__(self, *args, **kwargs):
        self.account_name = kwargs.pop('account_name',  setting("AZURE_ACCOUNT_NAME"))
        self.account_key = kwargs.pop('account_key', setting("AZURE_ACCOUNT_KEY"))
        self.azure_container = kwargs.pop('azure_container', setting("AZURE_CONTAINER"))
        super(AzureStorage, self).__init__(*args, **kwargs)
        self._connection = None
        

    @property
    def connection(self):
        if self._connection is None:
            self._connection = azure.storage.BlobService(
                self.account_name, self.account_key)
        return self._connection

    def _open(self, name, mode="rb"):
        return AzureBlockBlobFile(self.connection, self.azure_container, name, mode)

    def exists(self, name):
        try:
            p = self.properties(name)
        except azure.WindowsAzureMissingResourceError:
            return False
        else:
            return True

    def delete(self, name):
        self.connection.delete_blob(self.azure_container, name)

    def _save(self, name, content):
        f = self._open(name,'wb')
        cur = 0
        while True:
            data = content.read(self.chunk_size)
            if not len(data): break
            f.write(data)
        f.close()
        return name
       
    def url(self, name):
        return "https://%s%s/%s/%s" % (self.account_name, azure.BLOB_SERVICE_HOST_BASE, self.azure_container, name)
    
    def properties(self,name):
        return self.connection.get_blob_properties(
            self.azure_container, name)
        
    def size(self, name):
        return self.properties(name)["content-length"]

    def get_available_name(self,name):
        dir_path, file_name = os.path.split(name)
        name = clean_name(name)
        try:
            file_root, file_ext = re.match('^([^\.\s]+)(\.\S+)$',file_name).groups()
        except AttributeError:
            file_root, file_ext = (file_name,'')
        path_prefix = pathjoin(dir_path,file_root)
        file_list = {f.name: True for f in self.connection.list_blobs(self.azure_container,path_prefix)}
        ct = itertools.count(1)
        while name in file_list:            
            name = path_prefix + "_%s%s" % (next(ct),file_ext)
        return name


class AzureBlockBlobFile(RawIOBase):

    def __init__(self,connection,container,name,mode):
        name = clean_name(name)
        self.connection = connection
        self.name = name
        self.container = container
        self.mode = mode
        self._properties = None
        if 'w' in mode:
            try:
                self.properties
                if 'a' not in mode:
                    raise Exception("File Already Exists.")               
            except azure.WindowsAzureMissingResourceError as e:
                res = self.connection.put_blob(self.container,self.name,'',"BlockBlob")
        self._cur = 0
        self._end = (int(self.properties['content-length']) - 1) if int(self.properties['content-length']) > 0 else 0
        self._block_list = []
        

    @property
    def properties(self):
        if self._properties is None:
            self._properties=self.connection.get_blob_properties(
                  self.container,self.name)
        return self._properties

    def seek(self,pos):
        self.flush()
        if pos > self._end:
            raise Exception("Cannot seek past end of file")
        self._cur = pos

    def read(self,num_bytes=65536):
        start = self._cur
        end = self._cur+num_bytes-1
       
        if self._cur > self._end:
            raise Exception("Something odd happened.")
        if self._cur == self._end:
            return None
        if self._end < end:
            end = self._end
        content = self.connection.get_blob(self.container,self.name,
                                           x_ms_range='bytes=%d-%d' % (start, end))       
        self._cur = self._cur + len(content) if self._cur < self._end else self._end
        return content
    
    def write(self,data):
        blockid = "%6d" % len(self._block_list)
        try:
            self.connection.put_block(self.container, self.name, data, blockid)
            self._block_list.append((blockid,len(data)))
            return len(data)
        except WindowsAzureError as e:
            raise e
       
    def flush(self):
        if self._block_list:
            res = self.connection.put_block_list(self.container,self.name,[b[0] for b in self._block_list])
            self._end = sum([b[1] for b in self._block_list]) - 1
            self._cur = 0
            self._block_list = []
            
    def close(self):
        self.flush()

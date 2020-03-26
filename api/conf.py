## MongoDB configuration

# configuration for the db name
DB = 'test'

# configuration for the db host
MONGODB_HOST = 'mongodb://127.0.0.1:27017'
# MONGODB_HOST = mongodb+srv://mubi:1234@cluster001-avto2.mongodb.net/test?retryWrites=true&w=majority

## Filestorage configuration

# configuration for the path of the storage folder
STORAGE_FOLDER = 'C:/Dev/Python/withchartsapi_v0.2.5/storage/'
# STORAGE_FOLDER = '/home/mubashir/python/withchartsapi_v0.2.5/storage/'

# configuration for the allowed file extensions
ALLOWED_EXTENSION = ['.xls','.csv','.xlsx']

# configuration for the maximum file size in bytes (currently value: 20MB)
MAX_FILE_SIZE = 20971520

# configuration for the default deck's name
DEFAULT_DECK_NAME = 'Untitled Deck'

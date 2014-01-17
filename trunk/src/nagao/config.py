Config = {
    #### run as a daemon or not
    'daemonize' : True,

    #### read copus file
    'read_corpus_file' : False,
    
    #### the place where this file and main.py are.
    'main_directory': '/home/mahmoud/workspace/sentence detection huge database/',
    
    #### job_type = {batch_process, single_doc, , store_ngrams_on_file, tfidf, normalize_corpus}
    'job_type':'store_ngrams_on_file',

    #### ask for deleting previuos data from database
    'ask_delete_db': True,

    #### dbtype  mongo or redis
    'dbtype': 'redis',

    #### chunk_size
    'chunk_size':100,

    #### corpus_filename
    'corpus_filename':'fars+crawler+nasim_normalized.txt',    

    #### Nagao internal parameters
    'nagao':{
        'ngram_range' : 9,
        'sort_parameter' : 95
    },
        
    #### number_of_documents_in_corpus for tfidf.
    'number_of_documents_in_corpus' : 'Not set yet',
    
    #### mongodb
    'mongodb':{
        'dbname' : 'nagao',
        'collection' : 'ngrams'
    },

    #### redis
    'redis':{
        'db':'1',
        'port' : 6379,
        'host':'127.0.0.1'
    }
}

from datetime import datetime
run_time = datetime.now()
def log(text):
    pass
    #f = open (Config['main_directory'] + 'log/log' + str(run_time), 'aw')
    #f.writelines(str(datetime.now()) + ':  ' + text + '\r\n')
    #f.close()
    
    
    
    
    

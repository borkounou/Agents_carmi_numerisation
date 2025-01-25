
#!/bin/bash

set -eu

if [ "$APP_DEBUG" == 'True' ] ; then
  reload_opt='--reload'
else
  reload_opt=''
fi



sleep 5

/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -t 250 -b 0.0.0.0:5000 main:app --reload #$reload_opt 

# /usr/local/bin/gunicorn -w $NB_WORKERS -k uvicorn.workers.UvicornWorker -t 120 -b 0.0.0.0:5000 main:app --reload #$reload_opt 


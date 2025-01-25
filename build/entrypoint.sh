
#!/bin/bash

set -eu

if [ "$APP_DEBUG" == 'True' ] ; then
  reload_opt='--reload'
else
  reload_opt=''
fi



sleep 5

/usr/local/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -t 250 -b 0.0.0.0:8000 main:app $reload_opt 



# gunicorn --workers=<整數> --threads=<整數> <wsgi檔名>:<app名稱> 
if [ -z "$1" ]; then
  echo "Usage: $0 <port>"
  exit 1
fi
cd backend
if [ ! -d "logs/" ]; then
  mkdir -p "logs/"
fi
gunicorn -b 0.0.0.0:$1 --workers=4 --threads=4 server:app \
  --access-logfile logs/gunicorn_access.log \
  --error-logfile logs/gunicorn_error.log

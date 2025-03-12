if [ -z "$1" ]; then
    echo "Please input listen port!"
    exit
fi
echo "Starting Scoreboard Server on port $1"
npx http-server src/ -p $1 -S -C cert/cert.pem -K cert/key.pem

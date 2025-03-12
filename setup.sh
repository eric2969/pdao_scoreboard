echo "Node js installing..."
sudo apt update
sudo apt upgrade
sudo apt install nodejs npm tmux
echo "Node js installed successfully!"
echo "Updating scoreboard data..."
cd BuildTool
python3 BuildTool.py
cd ../
echo "Scoreboard data updated successfully!"
echo "Building scoreboard website data..."
npm install
npm audit fix
npm run build
echo "Generating TLS/SSL certificates..."
mkdir cert
openssl req -x509 -newkey rsa:2048 -keyout cert/key.pem -out cert/cert.pem -days 365 -nodes -subj "/C=TW/ST=Taiwan/L=Taipei/O=National Taiwan University/OU=National Taiwan University Department of Information Management/CN=49.158.179.101"
echo "Scoreboard constructed successfully!"

echo "Installing Dependencies..."
sudo apt update
sudo apt upgrade
sudo apt install nodejs npm tmux python3-flask python3-flask-cors python3-requests python3-hashlib gunicorn -y
echo "Dependencies installed successfully!"
echo "Initializing system data..."
cd BuildTool
python3 BuildTool.py
echo "System Data Initialized successfully!"
echo "Building scoreboard website data..."
npm install
npm audit fix
npm run build
echo "Scoreboard constructed successfully!"

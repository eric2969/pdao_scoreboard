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
echo "Scoreboard constructed successfully!"
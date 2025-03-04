echo "Node js installing..."
sudo apt update
sudo apt upgrade
sudo apt install nodejs npm tmux
echo "Node js installed successfully!"
echo "Installing scoreboard data..."
npm install
npm audit fix
npm run build
echo "Scoreboard data installed successfully!"
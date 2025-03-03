echo "Node js installing..."
sudo apt update
sudo apt upgrade
sudo apt install nodejs npm tmux
echo "Node js installed successfully!"
echo "Installing scoreboard data..."
npm install
npm audit fix
npm run build
ehco "Making new alias for scoreboard server..."
echo "alias scoreboard_con='tmux attach -t scoreboard_server'" >> ~/.bashrc
source ~/.bashrc
echo "Scoreboard data installed successfully!"
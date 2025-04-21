PDAO Scoreboard & Admin Webapp
================

Build Instruction
-----------------

First, install a modern verison of node.js (node 6.0+ and [nvm][nvm] is highly recommended).
After activating a node environment, we can install the dependencies.

Then you need to install python3 and its packages, and you also need to install wsgi production server for flask.


If you work on Linux, you can simply use the command `./setup.sh` to establish the environment.
If not, you can use the following to build the application:
```
sudo apt install nodejs npm python3-flask python3-flask-cors python3-requests gunicorn -y
npm install;npm run build
```

Then you need to build the contest data by the Buildtool, make sure use have check the csv file the folder:
```
cd BuildTool;python3 BuildTool.py
```
How to deploy scoreboard and admin server:
- Scoreboard:
    
    The directory `dist/` will contain the file tree of the built web application,
    which can be served using *static* web servers.
    For web servers, we recommend [`http-server -c-1`][http-server] (disable cache) or [nginx][nginx] or apache server.

    For development, try `npm start --verbose`.
- Admin and api for scoreboard:

    The directory `backend/` will contain the webapp for admin and api. If you are on Linux, you can simply use the shell script `start.sh ${listen port}` in the root folder, and you can stop the server by the `stop_server.sh`

    If you want to start the server without using the script, you can simply use the command in the directory `backend/`
    ```
    gunicorn -b 0.0.0.0:${listen port} --workers=8 --threads=8 server:app
    ```

    For development, you can use `python3 run.py` in the directory `backend/`

The scoreboard webapp is adapted from [Spotboard](https://github.com/spotboard/spotboard)

[nvm]: https://github.com/creationix/nvm
[http-server]: https://www.npmjs.com/package/http-server
[nginx]: http://nginx.org/
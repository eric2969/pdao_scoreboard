Spotboard Webapp
================

Build Instruction
-----------------

First, install a modern verison of node.js (node 6.0+ and [nvm][nvm] is highly recommended).
After activating a node environment, we can install the dependencies.
If you work on Linux, you can simply use the command `./setup.sh` to establish the environment.
If not, you can use the following to build the application:
```
npm install;npm run build
```
Then you need to build the contest data by the Buildtool, make sure use have check the csv file the folder:
```
cd BuildTool;python3 BuildTool.py
```

The directory `dist/` will contain the file tree of the built web application,
which can be served using *static* web servers.
For web servers, we recommend [`http-server -c-1`][http-server] (disable cache) or [nginx][nginx].

For development, try `npm start --verbose`.


[nvm]: https://github.com/creationix/nvm
[http-server]: https://www.npmjs.com/package/http-server
[nginx]: http://nginx.org/

penaltyTime can be adjusted in the first line of ./js/contest.js
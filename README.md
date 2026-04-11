Starting this project was a really lovely goal. 

First once i started, i found a real issue, carla 9.13 works on python 3.7, but on my system it is 3.12, and this is really mismatch.
I could find this in `PythonAPI/carla/dist/carla....egg` file, can you see py.3.7 one

and this is the cmd i was advised to use to run carla in low quality `.\CarlaUE4.exe -quality-level=Low -windowed -ResX=800 -ResY=600 -logs -RenderOffScreen`
* `-logs` create logs file to tracking if there is any issues
* `-RenderOffScreen` stop rendering so only physics engine is working

Now the first thing i started creating, it creating conda env, with python `3.7` to match carla python version. 
Then i installed carla package from carla directory, running pip install `.whl` path. 

and thing which is see is the most important is trying to open carla on my machine, it worked fine, no freezing, but GPU temp was at 70. i tried no rendering flag, it was fine, but alot of fatal error were happening, and carla was crashing, then i tried syncronous feature of carla, with `-benchmark` and `-fbs=20` flags to keep gpu. it worked fine.

Physics initialization artifact, when an object respawn at any world, it shows some physics values, we remove them. 
The solution is two things here, either filtering data later, or just wait couple of seconds until object respawn and then start collecting. it is call **warmup period**
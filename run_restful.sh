sudo docker run -d \
    --name restful \
    --restart=unless-stopped \
    --privileged --net=host \
    -v /home/pi/pi_restful:/usr/src/myapp \
    -w /usr/src/myapp \
    restful \
    python main.py

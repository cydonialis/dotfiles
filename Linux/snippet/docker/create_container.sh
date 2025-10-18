docker run -u $(id -u $USER):$(id -g $USER) --privileged --net=host -it \
    -v /home/$USER:/home/$USER \
    --name ubuntu22.04 \
    --ipc=host \
    --restart=always \
    ubuntu:22.04 \
    /bin/bash

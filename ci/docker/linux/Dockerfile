ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user
ARG CMAKE_DOWNLOAD_URL=https://github.com/Kitware/CMake/releases/download/v3.17.3/cmake-3.17.3-Linux-x86_64.sh
RUN wget -O /tmp/install_cmake.sh $CMAKE_DOWNLOAD_URL
RUN chmod +x /tmp/install_cmake.sh  && /tmp/install_cmake.sh  --skip-license
RUN apt update && apt install -y ninja-build
RUN python -m pip install pip --upgrade && pip install wheel sphinx tox pytest coverage pytest-cov lxml mypy flake8 devpi-client
USER user
WORKDIR /home/user

FROM python:3.9.9-slim

ENV AWS_SAM_VER=1.36.0
ENV AWS_SAM_SUM="48866227639fb8eda1b4f5445fe7f7e99f006a7a908cc1744dd21dc0e6442a3e"

RUN case $(uname -m) in \
    x86_64) SM_ARCH=64bit; CW_ARCH=amd64 ;; \
    aarch64) SM_ARCH=arm64; CW_ARCH=arm64 ;; \
    *) echo "UNKNOWN ARCH: $(uname -m)"; exit 1 ;; \
    esac \
 && sed -i 's:^path-exclude /usr/share/groff/\*::' /etc/dpkg/dpkg.cfg.d/docker \
 && apt-get update \
 && apt-get install -y git wget curl nmap zsh groff vim entr sudo jq parallel unzip make \
 && sed -i 's/^%sudo.*/%sudo ALL=(ALL) NOPASSWD: ALL/' /etc/sudoers \
 && pip install --upgrade pip \
 && pip install awscli \
 && curl https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_${SM_ARCH}/session-manager-plugin.deb -o /tmp/session-manager-plugin.deb \
 && dpkg -i /tmp/session-manager-plugin.deb \
 && rm /tmp/session-manager-plugin.deb \
 && sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
 && curl -Lo /cw.deb https://github.com/lucagrulla/cw/releases/download/v4.0.6/cw_${CW_ARCH}.deb \
 && dpkg -i /cw.deb \
 && rm -f /cw.deb \
 && wget -O /sam.zip "https://github.com/aws/aws-sam-cli/releases/download/v${AWS_SAM_VER}/aws-sam-cli-linux-x86_64.zip" \
 && echo "$AWS_SAM_SUM  /sam.zip" | sha256sum -c - \
 && unzip /sam.zip -d /sam-install \
 && /sam-install/install \
 && rm -Rf /sam.zip /sam-install \
 && sam --version

COPY status_board/requirements.txt /build/
RUN pip install -Ur /build/requirements.txt --no-cache-dir

# COPY scripts/docker_bashrc.sh /home/user/.bashrc
COPY scripts/docker_zshrc.sh /home/user/.zshrc
COPY scripts/docker_profile.sh /etc/profile.d/docker_dev.sh
COPY scripts/docker_launch.sh /launch.sh


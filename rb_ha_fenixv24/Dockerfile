ARG BUILD_FROM
FROM $BUILD_FROM
USER root

RUN \
    set -x \ 
    && apk add --no-cache \
        openssh \
        autossh 
        # add whatever dependencies you need

COPY run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
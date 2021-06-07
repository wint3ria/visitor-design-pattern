FROM daskdev/dask:2021.4.1 as runtime
ARG MODEL_NAME="the_visitors"
ARG REGISTRY_AUTH_TOKEN
ARG RT_SCENARIO_VERSION=1.0.4
ARG RTM_ADAPTER_VERSION=1.0.6
ARG RT_RESULTS_VERSION==1.0.0

WORKDIR /install

RUN pip install rtm-adapter-interface==${RTM_ADAPTER_VERSION} --extra-index-url https://__token__:${REGISTRY_AUTH_TOKEN}@gitlab.rayference.dansaert.be/api/v4/projects/150/packages/pypi/simple --trusted-host gitlab.rayference.dansaert.be --verbose
RUN pip install rt-scenario==${RT_SCENARIO_VERSION} --extra-index-url https://__token__:${REGISTRY_AUTH_TOKEN}@gitlab.rayference.dansaert.be/api/v4/projects/152/packages/pypi/simple --trusted-host gitlab.rayference.dansaert.be --verbose
RUN pip install rt-results==${RT_RESULTS_VERSION} --extra-index-url https://__token__:${REGISTRY_AUTH_TOKEN}@gitlab.rayference.dansaert.be/api/v4/projects/158/packages/pypi/simple --trusted-host gitlab.rayference.dansaert.be --verbose

COPY ./dist/${MODEL_NAME}-*.tar.gz ./
RUN /opt/conda/bin/pip install ./${MODEL_NAME}-*.tar.gz

WORKDIR /app

ENV MODEL_NAME=${MODEL_NAME}

ENTRYPOINT ["tini", "-g", "--", "/usr/bin/prepare.sh"]

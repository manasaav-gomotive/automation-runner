FROM eclipse-temurin:17-jdk-jammy

ARG DEBIAN_FRONTEND=noninteractive
ARG FRAMEWORK_REPO_URL=https://github.com/KeepTruckin/motive-testing-automationframework.git
ARG FRAMEWORK_REF=master
ARG GH_PAT=

ENV RUNNER_DIR=/opt/automation-runner \
    FRAMEWORK_DIR=/opt/motive-testing-automationframework \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip" \
    && unzip -q /tmp/awscliv2.zip -d /tmp \
    && /tmp/aws/install \
    && rm -rf /tmp/aws /tmp/awscliv2.zip

WORKDIR /opt

COPY . ${RUNNER_DIR}

RUN if [ -s "${RUNNER_DIR}/requirements.txt" ]; then python3 -m pip install --no-cache-dir -r "${RUNNER_DIR}/requirements.txt"; fi

RUN if [ -n "${GH_PAT}" ]; then \
      git clone --branch "${FRAMEWORK_REF}" "https://${GH_PAT}@${FRAMEWORK_REPO_URL#https://}" "${FRAMEWORK_DIR}"; \
    else \
      git clone --branch "${FRAMEWORK_REF}" "${FRAMEWORK_REPO_URL}" "${FRAMEWORK_DIR}"; \
    fi

RUN chmod +x "${RUNNER_DIR}/scripts/generate_framework_env.sh" "${RUNNER_DIR}/docker/test-runner-entrypoint.sh"

WORKDIR ${RUNNER_DIR}

ENTRYPOINT ["/opt/automation-runner/docker/test-runner-entrypoint.sh"]
CMD ["python3", "runner.py", "staging", "safety.settings"]

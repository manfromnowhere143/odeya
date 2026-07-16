#!/usr/bin/env bash
# Source this file before any release-lineage Git operation. It removes ambient
# repository routing and configuration while deliberately preserving an
# operator-controlled SSH agent and explicit GIT_ASKPASS.

unset \
  GIT_ALTERNATE_OBJECT_DIRECTORIES \
  GIT_ATTR_SOURCE \
  GIT_CEILING_DIRECTORIES \
  GIT_COMMON_DIR \
  GIT_CONFIG \
  GIT_CONFIG_GLOBAL \
  GIT_CONFIG_NOSYSTEM \
  GIT_CONFIG_PARAMETERS \
  GIT_CONFIG_SYSTEM \
  GIT_CURL_VERBOSE \
  GIT_DIR \
  GIT_DISCOVERY_ACROSS_FILESYSTEM \
  GIT_EXEC_PATH \
  GIT_EXTERNAL_DIFF \
  GIT_GRAFT_FILE \
  GIT_IMPLICIT_WORK_TREE \
  GIT_INDEX_FILE \
  GIT_NAMESPACE \
  GIT_NO_REPLACE_OBJECTS \
  GIT_OBJECT_DIRECTORY \
  GIT_PAGER \
  GIT_PREFIX \
  GIT_QUARANTINE_PATH \
  GIT_REPLACE_REF_BASE \
  GIT_SHALLOW_FILE \
  GIT_SSL_CAINFO \
  GIT_SSL_CAPATH \
  GIT_SSL_CERT \
  GIT_SSL_CERT_PASSWORD_PROTECTED \
  GIT_SSL_CIPHER_LIST \
  GIT_SSL_KEY \
  GIT_SSL_NO_VERIFY \
  GIT_SSL_VERSION \
  GIT_SSH \
  GIT_SSH_COMMAND \
  GIT_SSH_VARIANT \
  GIT_TRACE \
  GIT_TRANSPORT_HELPER_DEBUG \
  GIT_WORK_TREE

# GIT_CONFIG_COUNT=0 makes injected key/value pairs inert. Remove them and all
# Git trace destinations as well so nested transports cannot emit credentials
# or repository bytes through an attacker-selected file descriptor or socket.
while IFS= read -r odeya_git_environment_variable; do
  unset "$odeya_git_environment_variable"
done < <(
  compgen -A variable GIT_CONFIG_KEY_ || true
  compgen -A variable GIT_CONFIG_VALUE_ || true
  compgen -A variable GIT_TRACE_ || true
  compgen -A variable GIT_TRACE2 || true
)
unset odeya_git_environment_variable

export GIT_ATTR_NOSYSTEM=1
export GIT_CONFIG_COUNT=0
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_NO_REPLACE_OBJECTS=1
export GIT_PAGER=cat
export GIT_TERMINAL_PROMPT=0

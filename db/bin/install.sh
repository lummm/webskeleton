#!/bin/bash


DEF_BASE_DIR="${THIS_DIR}/schema"

FORCE="$1"
ATTEMPTS="10"

alias psql="psql -h ${PGHOST} -U ${PGUSER} --password ${PGPASSWORD}"


ERRS="1"
execute_all_sql_at_root() {
    if [ ! -d "${1}" ]; then
        return
    fi
    for f in $(find "${1}" -name '*.sql'); do
        psql -f "${f}" -v ON_ERROR_STOP=1
        if [[ ! "$?" == "0" ]]; then
            printf "\n\n---------------------- ERR\n"
            echo "${f}"
            printf "\n---------------------- ERR\n\n"
            ERRS="1"
        else
            echo "${f}"
        fi
    done
}

check_clean() {
    VSN_TABLE_EXISTS=$(psql -t -c "SELECT 1 FROM information_schema.tables WHERE table_name = 'vsn';")
    if [[ "${VSN_TABLE_EXISTS}" == "" ]]; then
        return
    fi
    EXISTING_VSN=$(psql -t -c "SELECT 1 FROM vsn;")
    if [[ ! "${EXISTING_VSN}" == "" ]] && [[ "${FORCE}" == "" ]] ; then
        echo "CAN'T INSTALL, DB HAS EXISTING INSTALL"
        exit 1
    fi
}


run_install() {
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/extensions
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/schemas
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/types
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/tables
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/views
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/functions

    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/data/permission
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/data/license
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/data/user
    execute_all_sql_at_root ${DEF_BASE_DIR}/internal/data/other

    execute_all_sql_at_root ${DEF_BASE_DIR}/sys

    execute_all_sql_at_root ${DEF_BASE_DIR}/api
}

install_with_retries() {
    attempt="1"
    while [[ "${ERRS}" == "1" ]]; do
        printf "\n\n\n\n------------  INSTALL ATTEMPT ${attempt} ----------\n\n\n\n\n"
        ERRS="0"
        run_install
        attempt=$((attempt+1))
        if [[ ${attempt} -gt ${ATTEMPTS} ]]; then
            exit 1
        fi
    done
    printf "\n\nDB INSTALL SUCCESS\n\n\n"
}

save_vsn() {
    if [[ "${GIT_REV}" == "" ]]; then
        GIT_REV=$(git rev-parse --verify HEAD)
    fi
    psql -c "INSERT INTO vsn (git_rev) VALUES ( '${GIT_REV}' )"
}

if [[ "${FORCE}" == "" ]]; then
    check_clean
fi
install_with_retries
save_vsn

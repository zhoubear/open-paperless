#!/bin/bash
set -e

# Source: https://github.com/sameersbn/docker-gitlab/
map_uidgid() {
    USERMAP_ORIG_UID=$(id -u mayan)
    USERMAP_ORIG_UID=$(id -g mayan)
    USERMAP_GID=${USERMAP_GID:-${USERMAP_UID:-$USERMAP_ORIG_GID}}
    USERMAP_UID=${USERMAP_UID:-$USERMAP_ORIG_UID}
    if [[ ${USERMAP_UID} != "${USERMAP_ORIG_UID}" || ${USERMAP_GID} != "${USERMAP_ORIG_GID}" ]]; then
        echo "Mapping UID and GID for mayan:mayan to $USERMAP_UID:$USERMAP_GID"
        groupmod -g "${USERMAP_GID}" mayan
        sed -i -e "s|:${USERMAP_ORIG_UID}:${USERMAP_GID}:|:${USERMAP_UID}:${USERMAP_GID}:|" /etc/passwd
    fi
}

set_permissions() {
    # Set permissions for application directory
    chown -Rh mayan:mayan /usr/src/mayan
}

install_languages() {
    local langs="$1"
    read -ra langs <<<"$langs"

    # Check that it is not empty
    if [ ${#langs[@]} -eq 0 ]; then
        return
    fi

    # Update apt-lists
    apt-get update

    # Loop over languages to be installed
    for lang in "${langs[@]}"; do
        pkg="tesseract-ocr-$lang"
        if dpkg -s "$pkg" > /dev/null 2>&1; then
            continue
        fi

        if ! apt-cache show "$pkg" > /dev/null 2>&1; then
            continue
        fi

        apt-get install "$pkg"
    done

    # Remove apt lists
    rm -rf /var/lib/apt/lists/*
}

initial_setup() {
    sudo -HEu mayan "/usr/src/mayan/manage.py" "createsettings"
    sudo -HEu mayan "/usr/src/mayan/manage.py" "migrate" "--no-input"
    sudo -HEu mayan "/usr/src/mayan/manage.py" "createautoadmin"
}

upgrade() {
    sudo -HEu mayan "/usr/src/mayan/manage.py" "collectstatic" "--no-input"
    sudo -HEu mayan "/usr/src/mayan/manage.py" "migrate" "--no-input"
    sudo -HEu mayan "/usr/src/mayan/manage.py" "purgeperiodictasks"
}

append_settings() {
    if [[ -f /tmp/settings.conf ]]; then
        cat /tmp/settings.conf >> mayan/settings/base.py
    fi
}

if [[ "$1" != "/"* ]]; then
    map_uidgid
    set_permissions

    # Install additional languages if specified
    if [ ! -z "$OCR_LANGUAGES"  ]; then
        install_languages "$OCR_LANGUAGES"
    fi

    sudo -HEu mayan ". /usr/share/mayan/venv/bin/activate"

    if [ ! -f mayan/media/db.sqlite3 ]; then
        initial_setup
    else
        upgrade
    fi

    #append_settings

    exec sudo -HEu mayan "/usr/src/mayan/manage.py" "$@"
fi

exec "$@"

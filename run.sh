#!/usr/bin/with-contenv bashio

declare configuration_file

configuration_file=$(bashio::config 'configuration_file')
if ! bashio::fs.file_exists "${configuration_file}"; then
    bashio::log.fatal
    bashio::log.fatal "Seems like the configured configuration file does"
    bashio::log.fatal "not exists:"
    bashio::log.fatal
    bashio::log.fatal "${configuration_file}"
    bashio::log.fatal
    bashio::log.fatal "Please check the add-on configuration, or create the"
    bashio::log.fatal "configuration file."
    bashio::exit.nok
fi

bashio::log.info "Starting MQTT Accumulator..."
python3 -u /tmp/main.py "$(bashio::config 'configuration_file')"

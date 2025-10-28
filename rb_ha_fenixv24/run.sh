#!/usr/bin/with-contenv bashio

# LOG: Initialising
bashio::log.info "Reverse tunnel initializing."

# GET values from config
username=$(bashio::config 'username')
host=$(bashio::config 'server.host')

# GET values from API for temperature

# SET sensors for homeassistant to use

# LOG: Show values
bashio::log.info "Reverse tunnel configured for $username@$host"

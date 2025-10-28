#!/usr/bin/with-contenv bashio

# LOG: Initialising
bashio::log.info "Fenix V24 initialising."

# GET values from config
username=$(bashio::config 'email')
host=$(bashio::config 'password')
smarthome_id=$(bashio::config 'smarthome_id')

# GET values from API for temperature

# SET sensors for homeassistant to use

# LOG: Show values
bashio::log.info "Fenix v24 configured for $email@$smarthome_id"

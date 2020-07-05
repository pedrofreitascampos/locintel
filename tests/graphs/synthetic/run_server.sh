#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

usage()
{
    cat << USAGE >&2
Usage:
    Script has mandatory arguments (three arguments in case no traffic and five arguments in case traffic is enabled)
    ./routingService.sh processData startServer needTraffic injectMode trafficFileName
        - processData (required): {true|false}; whether to prepare data for the server
        - startServer (required): {true|false}; whether to run the server
        - needTraffic (required): {true|false}; defines whether traffic files shall be applied
        - injectMode (optional): {true|false}; If true, a traffic updated is applied on an already running
          instance of routing-service. If false, a new routing-service will start with the given traffic file.
        - trafficFileName (optional): relative path to the traffic file from ${localDataFolder}.

    It is required to provide your map data as ${localDataFolder}/${localosmname}.osm.pbf.
USAGE
    exit 1
}

readonly processData=$1
readonly startServer=$2
readonly enableTraffic=$3

# Variables that could be changed
readonly localDataFolder=data
readonly luaProfile=car
readonly containerDataFolder=/data
readonly serviceName=local-routing-service
port=5000
localosmname=data

# Constants that not make sense to change
readonly image=registry.mobilityservices.io/am/roam/routing-service/develop:latest
readonly osrmPath=./node_modules/osrm/lib/binding
readonly dockerCmd="docker run -t --rm -v ${PWD}/${localDataFolder}:${containerDataFolder} ${image}"
readonly luaPath=node_modules/osrm/profiles/${luaProfile}.lua

i=1
for arg do
    case $arg in
        -f | --input-file )     paramindex=$((i+1))
                                localosmname=${!paramindex}
                                ;;
        -p | --port )           paramindex=$((i+1))
                                port=${!paramindex}
                                ;;
        -h | --help )           usage
                                exit
                                ;;
    esac
    i=$((i + 1))
done

# This paths comes from routing service config file ( default.js ), changing them will break the script
readonly appData=/home/node/app/data/app
readonly osmPbfData=${containerDataFolder}/${localosmname}.osm.pbf
readonly osrmData=${containerDataFolder}/${localosmname}.osrm

echo $processData

if [[ $# -lt 3 ]]; then
    echo "Error: you need to provide all arguments. See usage"
    usage
fi

if [ ! -f "${localDataFolder}/${localosmname}.osm.pbf" ]; then
    echo "Required ${localDataFolder}/${localosmname}.osm.pbf file doesn't exist"
    usage
fi

runServer() {
    docker run --name ${serviceName} -p ${port}:5000 --rm -v ${PWD}/${localDataFolder}:${appData} ${image} npm start
}

prepareData() {
    ${dockerCmd} ${osrmPath}/osrm-extract -p ${luaPath} ${osmPbfData}
    ${dockerCmd} ${osrmPath}/osrm-partition ${osrmData}
    ${dockerCmd} ${osrmPath}/osrm-customize ${osrmData}
}

applyTraffic() {
    ${dockerCmd} ${osrmPath}/osrm-customize ${osrmData} --segment-speed-file ${containerDataFolder}/${trafficFile}
}

injectTraffic() {
    docker exec -it ${serviceName} ${osrmPath}/osrm-customize ${appData}/${localosmname}.osrm --segment-speed-file ${appData}/${trafficFile}
    docker exec -it ${serviceName} ${osrmPath}/osrm-datastore ${appData}/${localosmname}.osrm
}



if [ ! ${enableTraffic} == "true" ]; then
    echo "Traffic is disabled"

    if [ ${processData} == "true" ]; then
      echo "Prepare data"
      prepareData
    fi

    if [ ${startServer} == "true" ]; then
      echo "Run routing local service"
      runServer
    fi
    exit 0
fi

if [[ $# -lt 5 ]]; then
    echo "Error: you need to provide 5 arguments with enabled traffic. See usage"
    usage
fi

readonly injectMode=$4
readonly trafficFile=$5

if [ ! -f "${localDataFolder}/${trafficFile}" ]; then
    echo "With enabled traffic ${localDataFolder}/${trafficFile} file is mandatory"
    usage
fi

if [ ${injectMode} == "true" ]; then
        echo "Inject traffic data ${trafficFile}"
        echo "NOTE: you need to have running routing service to be able to inject new traffic data."
        injectTraffic
else
    if [ ${processData} == "true" ]; then
      echo "Prepare data"
      prepareData
    fi

    echo "Apply traffic file with ${trafficFile}"
    applyTraffic

    if [ ${startServer} == "true" ]; then
      echo "Run routing local service"
      runServer
    fi
fi
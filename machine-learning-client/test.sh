#!/usr/bin/bash

pushd example

time curl -X POST \  7 ↵
-H "Content-Type: audio/ogg" \
	--data-binary "@example/Colaptes_auratus.ogg" \
	http:127.0.0.1:5000/analyze

popd

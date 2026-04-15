
#!/usr/bin/bash

pushd example

time curl -X POST \
	-H "Content-Type: audio/ogg" \
	--data-binary "@Colaptes_auratus.ogg" \
	http://localhost:8000/analyze

popd

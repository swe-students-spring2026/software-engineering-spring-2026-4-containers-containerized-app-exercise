
#!/usr/bin/bash

pushd example

for i in {001..008}; do
    file="Colaptes_auratus_XC104536_$i.ogg"
    echo file

    curl -X POST \
        -H "Content-Type: audio/ogg" \
        --data-binary "@${file}"  \
        http://localhost:8000/analyze | jq
done

popd

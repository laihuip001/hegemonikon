#!/bin/bash
for file in $(python -m mekhane.dendron.cli check mekhane/ --ci --format ci | grep -o "mekhane/.*\.py"); do
    echo "Adding PROOF header to $file"
    if ! grep -q "# PROOF:" "$file"; then
        sed -i '1i# PROOF: [L2/Infra] <- mekhane/' "$file"
    fi
done

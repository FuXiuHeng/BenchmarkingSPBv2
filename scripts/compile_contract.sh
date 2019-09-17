#!/bin/bash
echo "var energy_trade = `solc --overwrite --combined-json abi,bin,interface contracts/energy_trade.sol`" > contracts/energy_trade.js
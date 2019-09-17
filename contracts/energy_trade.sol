// Specify which compiler version to compile this code with
pragma solidity >=0.4.0 <0.6.0;

contract EnergyTrade {
    struct Trade {
        address payable to;
        address from;
        uint value;
    }

    mapping (uint => Trade) tradeList;
    uint numTrades;

    constructor() public {
        numTrades = 0;
    }

    function commitValue(address payable to) public payable returns (uint tradeId) {
        tradeId = numTrades;
        Trade memory t = tradeList[tradeId];
        t.to = to;
        t.from = msg.sender;
        t.value = msg.value;
        numTrades++;
    }

    function confirmReceipt(uint tradeId) public {
        Trade memory t = tradeList[tradeId];
            t.to.transfer(t.value);
    }
}

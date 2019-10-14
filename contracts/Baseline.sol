pragma solidity >= 0.5.0;

contract Baseline {
    address payable producer;
    address consumer;
    uint tradeValue;
    uint curValue;

    constructor(address _consumer, uint _value) public {
        producer = msg.sender;
        consumer = _consumer;
        tradeValue = _value;
    }

    function makePayment() public payable {
        uint value = msg.value;
        curValue += value;
    }

    function confirmReceipt() public payable {
        address from = msg.sender;
        if (from == consumer && curValue >= tradeValue) {
            producer.transfer(tradeValue);
        }
    }

    function isPaid() public view returns(bool) {
        return (curValue >= tradeValue);
    }
}
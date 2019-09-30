pragma solidity >=0.5.0;

contract Baseline {
    struct Payment {
        address from;
        address payable to;
        uint value;
    }

    mapping (uint => Payment) commitments;
    uint numCommitments;

    constructor() public {
        numCommitments = 0;
    }

    function commitMoney(address payable to) public payable returns (uint) {
        address from = msg.sender;
        uint amount = msg.value;

        commitments[numCommitments] = Payment(from, to, amount);
        numCommitments++;

        return numCommitments;
    }

    function confirmReceipt(uint id) public payable {
        Payment memory p = commitments[id];
        p.to.transfer(p.value);
    }

    function getNum() public view returns(uint) {
        return numCommitments;
    }

}
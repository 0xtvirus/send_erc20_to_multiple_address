// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

import "./Interfaces/IERC20Minimal.sol";


contract sendTokenMultipleReciever_2 {
    address public owner;
    address public contractAddress;

    constructor() {
        owner = msg.sender;
        contractAddress = address(this);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "This function is restricted to the contract's owner");
        _;
    }

    function sendTokens(address _token, uint256 amount, address[] memory recipients) public onlyOwner {
        uint len = recipients.length;
        require (len > 0, "There is not any reciever");
        uint requiredTotalAmount = len * amount;
        uint ammountAtcontract = IERC20Minimal(_token).balanceOf(address(this));
        require (ammountAtcontract >= requiredTotalAmount, "Amount at sender is not enough !!!!");

        for (uint256 i = 0; i < len; i++) {
          IERC20Minimal(_token).transfer(recipients[i], amount);
        }
  }
}

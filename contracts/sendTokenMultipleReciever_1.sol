// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;
import "./Interfaces/IERC20Minimal.sol";

contract sendTokenMultipleReciever_1 {
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


  function send_token_multiple(address _token, uint _amount, address[] memory _recievers) public onlyOwner returns (string memory, uint, uint, uint) {
    uint len = _recievers.length;
    require (len > 0, "There is not any reciever");
    uint requiredTotalAmount = len * _amount;
    uint ammountAtsender = IERC20Minimal(_token).balanceOf(owner);
    require (ammountAtsender >= requiredTotalAmount, "Amount at sender is not enough !!!!");
    for (uint i=0; i<len; i++) {
          IERC20Minimal(_token).transferFrom(owner, _recievers[i], _amount);
    }

    return (IERC20Minimal(_token).symbol(), _amount, requiredTotalAmount, ammountAtsender);
  }
}

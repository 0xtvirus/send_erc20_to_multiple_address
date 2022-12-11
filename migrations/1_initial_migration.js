const Contract_1 = artifacts.require("sendTokenMultipleReciever_1");
// const Contract_2 = artifacts.require("sendTokenMultipleReciever_2");

module.exports = function (deployer) {
  deployer.deploy(Contract_1);
};

// module.exports = function (deployer) {
//   deployer.deploy(Contract_2);
// };

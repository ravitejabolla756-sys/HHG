import hre from "hardhat";
const { ethers } = hre;
const network = await ethers.provider.getNetwork();
if (network.chainId !== 80002n) {
  throw new Error(`Refusing deployment: expected Polygon Amoy chain ID 80002, received ${network.chainId}`);
}
const factory = await ethers.getContractFactory("VerificationRegistry");
const contract = await factory.deploy();
await contract.waitForDeployment();
const receipt = await contract.deploymentTransaction().wait();
console.log(`VerificationRegistry deployed at ${await contract.getAddress()}`);
console.log(`Deployment transaction: ${receipt.hash}`);
console.log(`Deployment block: ${receipt.blockNumber}`);

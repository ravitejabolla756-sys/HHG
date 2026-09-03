import "@nomicfoundation/hardhat-ethers";
import "dotenv/config";
export default {
  solidity: "0.8.24",
  networks: {
    amoy: {
      url: process.env.POLYGON_AMOY_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 80002,
    },
  },
};

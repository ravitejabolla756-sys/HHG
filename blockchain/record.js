import { ethers } from "ethers";
import "dotenv/config";
import { toContractPayload } from "./payload.js";
const abi = ["function registerVerification(bytes32 verificationHash,string sourceUrl,string platform) external", "function getVerification(bytes32 verificationHash) external view returns (string sourceUrl,string platform,uint64 timestamp,address submitter)", "event VerificationRegistered(bytes32 indexed verificationHash,string sourceUrl,string platform,uint64 timestamp,address indexed submitter)"];
export async function register(payload) {
  const provider = new ethers.JsonRpcProvider(process.env.POLYGON_AMOY_RPC_URL);
  const network = await provider.getNetwork();
  if (network.chainId !== 80002n) {
    throw new Error(`Refusing blockchain write: expected Polygon Amoy chain ID 80002, received ${network.chainId}`);
  }
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
  const contract = new ethers.Contract(process.env.CONTRACT_ADDRESS, abi, wallet);
  const contractPayload = toContractPayload(payload.hash.replace(/^0x/, ""), payload.source_url, payload.platform);
  const expectedHash = ethers.hexlify(contractPayload.hash).toLowerCase();
  const existingRecord = await contract.getVerification(expectedHash);
  if (existingRecord[2] > 0n) {
    const existingEvent = await findRegistrationEvent(contract, expectedHash, provider);
    if (!existingEvent) throw new Error("Existing verification record has no matching registration event");
    const receipt = await existingEvent.getTransactionReceipt();
    return buildResult({
      contract,
      contractPayload,
      expectedHash,
      eventHash: existingEvent.args.verificationHash,
      network,
      receipt,
      record: existingRecord,
      txHash: existingEvent.transactionHash,
      wallet,
      registrationStatus: "already_registered",
    });
  }

  const tx = await contract.registerVerification(contractPayload.hash, contractPayload.source_url, contractPayload.platform);
  const receipt = await tx.wait();
  const parsedEvent = receipt.logs
    .map((log) => {
      try { return contract.interface.parseLog(log); } catch { return null; }
    })
    .find((event) => event?.name === "VerificationRegistered");
  if (!parsedEvent) throw new Error("VerificationRegistered event was not found in the confirmed receipt");
  const record = await contract.getVerification(expectedHash);
  return buildResult({
    contract,
    contractPayload,
    expectedHash,
    eventHash: parsedEvent.args.verificationHash,
    network,
    receipt,
    record,
    txHash: tx.hash,
    wallet,
    registrationStatus: "registered",
  });
}

async function findRegistrationEvent(contract, verificationHash, provider) {
  const deploymentBlock = Number(process.env.CONTRACT_DEPLOYMENT_BLOCK);
  if (!Number.isSafeInteger(deploymentBlock) || deploymentBlock < 0) {
    throw new Error("CONTRACT_DEPLOYMENT_BLOCK must be configured for existing-record verification");
  }
  const filter = contract.filters.VerificationRegistered(verificationHash);
  for (let toBlock = await provider.getBlockNumber(); toBlock >= deploymentBlock; toBlock -= 10) {
    const fromBlock = Math.max(deploymentBlock, toBlock - 9);
    const events = await contract.queryFilter(filter, fromBlock, toBlock);
    if (events.length > 0) return events.at(-1);
  }
  return null;
}

async function buildResult({ contract, contractPayload, expectedHash, eventHash, network, receipt, record, txHash, wallet, registrationStatus }) {
  const onChainHash = eventHash.toLowerCase();
  const readBack = {
    sourceUrl: record[0],
    platform: record[1],
    timestamp: Number(record[2]),
    submitter: record[3],
  };
  const hashMatches = onChainHash === expectedHash;
  const readBackMatches = readBack.timestamp > 0
    && readBack.sourceUrl === contractPayload.source_url
    && readBack.platform === contractPayload.platform
    && readBack.submitter.toLowerCase() === wallet.address.toLowerCase();
  return {
    network: "Polygon Amoy",
    chainId: Number(network.chainId),
    registrationStatus,
    contractAddress: await contract.getAddress(),
    txHash,
    blockNumber: receipt.blockNumber,
    transactionConfirmed: receipt.status === 1,
    localHash: expectedHash,
    onChainHash,
    hashMatches,
    readBackMatches,
    record: readBack,
    explorerUrl: `${process.env.EXPLORER_BASE_URL || "https://amoy.polygonscan.com/tx/"}${txHash}`,
  };
}

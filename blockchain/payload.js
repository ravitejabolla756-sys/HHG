import { getBytes } from "ethers";

export function toContractPayload(sha256Hex, sourceUrl, platform) {
  if (!/^[0-9a-f]{64}$/i.test(sha256Hex)) throw new Error("Expected a 64-character SHA-256 hex digest");
  if (!/^https?:\/\//i.test(sourceUrl)) throw new Error("Source URL must be absolute");
  return { hash: getBytes(`0x${sha256Hex}`), source_url: sourceUrl, platform };
}

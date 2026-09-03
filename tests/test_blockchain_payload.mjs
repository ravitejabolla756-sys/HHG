import assert from "node:assert/strict";
import test from "node:test";
import { toContractPayload } from "../blockchain/payload.js";

test("constructs the exact bytes32 blockchain payload", () => {
  const payload = toContractPayload("a".repeat(64), "https://instagram.com/p/real", "instagram");
  assert.equal(payload.hash.length, 32);
  assert.equal(payload.source_url, "https://instagram.com/p/real");
  assert.equal(payload.platform, "instagram");
});

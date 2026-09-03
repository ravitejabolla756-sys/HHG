// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
contract VerificationRegistry {
    struct Record { string sourceUrl; string platform; uint64 timestamp; address submitter; }
    mapping(bytes32 => Record) private records;
    error AlreadyRegistered();
    event VerificationRegistered(bytes32 indexed verificationHash, string sourceUrl, string platform, uint64 timestamp, address indexed submitter);
    function registerVerification(bytes32 verificationHash, string calldata sourceUrl, string calldata platform) external {
        if (records[verificationHash].timestamp != 0) revert AlreadyRegistered();
        records[verificationHash] = Record(sourceUrl, platform, uint64(block.timestamp), msg.sender);
        emit VerificationRegistered(verificationHash, sourceUrl, platform, uint64(block.timestamp), msg.sender);
    }
    function getVerification(bytes32 verificationHash) external view returns (string memory sourceUrl, string memory platform, uint64 timestamp, address submitter) { Record memory r = records[verificationHash]; return (r.sourceUrl, r.platform, r.timestamp, r.submitter); }
}

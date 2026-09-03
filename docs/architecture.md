# Architecture

Python owns input hashing, local InsightFace detection/encoding, provider calls, parsing, selection, and canonical payload construction. Node/ethers owns the transaction and contract read-back. The embedding is held only in process memory and discarded after stage 3. The contract stores a hash-keyed record and emits an event; the hash prevents later payload tampering but does not prove identity or authorship of the source post.

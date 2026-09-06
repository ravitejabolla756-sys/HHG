# Known limitations

## Reverse-image-search coverage

SerpApi and Google Lens are external services. Availability, quotas, latency, response fields, ranking, and indexed-web coverage can change. A related public post may exist without appearing in a particular fresh search.

## Public-result stability

Social posts, pages, and provider thumbnails may be removed, made private, region-restricted, login-gated, or changed after verification. The blockchain record proves what metadata was submitted at a point in time; it does not preserve the remote content.

## Face comparison

InsightFace similarity is probabilistic. Results vary with resolution, compression, scale, crop, pose, lighting, expression, age, occlusion, and model/runtime versions. The `0.45` acceptance threshold is a conservative project rule, not universal biometric or legal identity proof.

A passing comparison demonstrates visual correspondence between the input face and a face in the provider-returned candidate thumbnail. It does not establish the person's name, legal identity, authorship, consent, account ownership, or control of the social profile.

## Candidate evidence

Candidates without a trusted, reachable, decodable thumbnail containing a detectable face fail closed. This avoids unsupported matches but can create false negatives. Public-web titles and metadata may be incomplete or wrong and are not used as identity evidence.

## Blockchain scope

Polygon Amoy is a public testnet. RPC availability, explorer indexing, confirmation time, and test tokens have no production guarantee. `VerificationRegistry` prevents duplicate hashes and makes recorded metadata tamper-evident, but it cannot independently validate the social URL, provider response, or off-chain biometric comparison.

## Ethical boundary

The pipeline is intended only for the repository owner's image, an explicitly consenting person, or clearly public imagery used appropriately. It must not be treated as a surveillance, doxxing, sensitive-trait inference, or automated identity-decision system.

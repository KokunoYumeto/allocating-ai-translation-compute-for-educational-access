# Synthetic Javanese audio

These are actual synthetic Javanese speech files, not human recordings. No Indonesian or English voice was substituted. Pronunciation and dialect suitability remain provisional and have not been human-certified.

| Track | Voice | Duration | Bytes | SHA-256 |
|---|---|---:|---:|---|
| `jv-academic` | `jv-ID-DimasNeural` (`jv-ID`) | 938.352 s | 7506836 | `d385c099cff28243252db4900172b88e3e3ed10898cc3b549eff4b93d23db591` |
| `jv-conversation` | `jv-ID-SitiNeural` (`jv-ID`) | 877.512 s | 7020116 | `027ddddcb4bfa472674152383bb92f676e8eec218345e63f5b2f2cc09e202f33` |

`AUDIO.json` binds each MP3 to its source-positioned SSML and spoken-text hashes and records the deterministic normalization replay. Routine offline rebuilds preserve these admitted bytes and do not contact the synthesis service.

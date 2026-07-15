# Retained upstream RFC 8785 author vectors

The encoded vectors in `vectors.json` are copied byte-for-byte, as hexadecimal,
from `testdata/input/*.json` and `testdata/output/*.json` at commit
`19d51d7fe467d4706a3ff08adf8a748f29fc21e0` of
<https://github.com/cyberphone/json-canonicalization>.

Copyright 2018 Anders Rundgren. Licensed under Apache License 2.0. The upstream
`LICENSE` notice is retained in this directory and points to
<https://www.apache.org/licenses/LICENSE-2.0>. No code from that repository is included;
only its conformance data is retained. Hex encoding preserves exact input and
expected-output bytes, including whether a source file ended with a newline.

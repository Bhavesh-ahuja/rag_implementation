import dns.resolver

print("Resolving SRV record for: _mongodb._tcp.rag-impli-cluster.v3a8tsj.mongodb.net")
try:
    answers = dns.resolver.resolve(
        "_mongodb._tcp.rag-impli-cluster.v3a8tsj.mongodb.net",
        "SRV"
    )

    for r in answers:
        print(f"SUCCESS: {r}")
except Exception as e:
    print(f"FAILURE: {e}")

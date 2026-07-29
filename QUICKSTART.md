# Quickstart

```bash
# install (Python 3.10+)
pip install -e ".[test]"

# run the suite — includes the Shanghai scenario end-to-end
pytest

# run the fly-with-a-token demo: allow → stale deny → blocked-country deny,
# evidence written as OSCAL assessment-results
opg demo

# validate every OSCAL file in data/ (and the generated evidence)
# against the vendored official NIST v1.1.3 schemas
opg validate

# optional: the same pipeline as a LangGraph StateGraph
pip install -e ".[graph]"
python -c "from oscal_presence_gate import build_langgraph; g = build_langgraph(); print(type(g))"
```

Change the policy without touching code: edit the parameters in
`data/profiles/restricted-transaction-baseline.json` (blocked countries,
attestation window, delegation TTL) and re-run `opg demo`.

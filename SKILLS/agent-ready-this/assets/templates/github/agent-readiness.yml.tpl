name: Agent readiness

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  validate-agent-artifacts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python .agents/skills/agent-ready-this/scripts/validate_artifacts.py --repo . --report agent-readiness-validation.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: agent-readiness-validation
          path: agent-readiness-validation.json

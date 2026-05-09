# Contributing to PRESTO-CORE

PRESTO-CORE is built for performance engineers who work on systems where failure has real consequences. Contributions are welcome from anyone who has lived the gap between performance requirements and performance tests.

## What we're looking for

- Bug fixes with test cases
- New load pattern implementations (the soak and stress patterns need work)
- Additional output generators (JMeter, NeoLoad)
- Results validator improvements
- Documentation improvements and real-world examples

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b your-feature-name`
3. Make your changes
4. Test against the examples in `/examples`
5. Submit a pull request with a clear description of what you changed and why

## Running the examples locally

```bash
# Install dependencies
pip install pyyaml

# Parse and generate from an example NFR
cd presto-core
python -c "
import sys
sys.path.insert(0, 'src')
from parser.nfr_parser import NFRParser
from generator.k6_generator import K6Generator

parser = NFRParser()
generator = K6Generator()
nfr = parser.parse_file('examples/payment-api.yaml')
print(generator.generate(nfr))
"
```

## Reporting bugs

Use the bug report template in `.github/ISSUE_TEMPLATE/bug_report.md`

Include your NFR YAML, the command you ran, and the error you got.

## Questions

Open an issue with your question. If it's about applying PRESTO to a specific system type, include a description of your system and what problem you're trying to solve.

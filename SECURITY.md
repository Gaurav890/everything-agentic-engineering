# Security policy

## Reporting a vulnerability

Do not open a public issue for an active vulnerability, leaked credential, or
exploit path.

Use GitHub's private vulnerability reporting for this repository. Include:

- affected files or versions;
- impact and prerequisites;
- reproduction steps or a minimal proof of concept;
- suggested remediation when known.

Do not access data that is not yours, degrade services, persist access, or
publish the vulnerability before maintainers have had a reasonable opportunity
to respond.

## Supported versions

Security fixes target the latest release and `main`. Until the first tagged
release, `main` is the only supported line.

## Agent and integration boundaries

Third-party skills, MCP servers, crawled content, generated code, and research
findings are untrusted inputs. Installing tools, expanding permissions, changing
credentials, deploying, modifying production data, or weakening a security gate
requires explicit human approval.

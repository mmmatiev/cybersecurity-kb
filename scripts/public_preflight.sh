#!/bin/zsh

set -eu

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

fail() {
  print -u2 -- "public_preflight=failed: $1"
  exit 1
}

for sensitive_path in \
  '.obsidian/plugins/obsidian-local-rest-api/data.json' \
  '.obsidian/workspace.json' \
  '.obsidian/workspace-mobile.json' \
  '.DS_Store'; do
  if git ls-files --error-unmatch -- "$sensitive_path" >/dev/null 2>&1; then
    fail "ignored sensitive path is tracked: $sensitive_path"
  fi
done

sensitive_names=$(git ls-files | rg -i '(^|/)(\.env($|\.)|id_rsa$|id_ed25519$)|\.(pem|p12|pfx|key)$' || true)
if [[ -n "$sensitive_names" ]]; then
  print -u2 -- 'Credential-shaped filenames in the index:'
  print -u2 -- "$sensitive_names"
  fail 'credential-shaped filenames require explicit review'
fi

quoted_credential_pattern="(api[_-]?key|access[_-]?token|client[_-]?secret|password|private[_-]?key)\s*(?::|(?<![=!<>])=(?!=))\s*[\"'][A-Za-z0-9_./+\-=]{16,}[\"']"
quoted_hits=$(git grep --cached -Il -i -P -e "$quoted_credential_pattern" -- || true)
if [[ -n "$quoted_hits" ]]; then
  print -u2 -- 'Credential-shaped assignments in tracked text (filenames only):'
  print -u2 -- "$quoted_hits"
  fail 'credential-shaped assignments require explicit review'
fi

environment_hits=$(git grep --cached -Il -P -e '^[[:space:]]*[A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD)[A-Z0-9_]*=[A-Za-z0-9_./+=-]{16,}[[:space:]]*$' -- || true)
if [[ -n "$environment_hits" ]]; then
  print -u2 -- 'Credential-shaped environment assignments in tracked text (filenames only):'
  print -u2 -- "$environment_hits"
  fail 'environment assignments require explicit review'
fi

pem_prefix='-----BEGIN '
pem_suffix='PRIVATE KEY-----'
pem_hits=$(git grep --cached -Il -E -e "${pem_prefix}(RSA |EC |OPENSSH )?${pem_suffix}" -- || true)
if [[ -n "$pem_hits" ]]; then
  print -u2 -- 'Private-key markers in tracked text (filenames only):'
  print -u2 -- "$pem_hits"
  fail 'private-key material must not be committed'
fi

oversized_files=$(
  while IFS= read -r -d $'\0' staged_path; do
    staged_size=$(git cat-file -s ":$staged_path")
    if (( staged_size >= 52428800 )); then
      print -r -- "$staged_path ($staged_size bytes)"
    fi
  done < <(git diff --cached --name-only --diff-filter=AM -z)
)
if [[ -n "$oversized_files" ]]; then
  print -u2 -- 'Staged files at or above 50 MiB:'
  print -u2 -- "$oversized_files"
  fail 'use Git LFS or external storage after a separate decision'
fi

git diff --cached --check

print -- 'public_preflight=ok'

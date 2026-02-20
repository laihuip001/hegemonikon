import os

def add_proof_header(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    if content.startswith('# PROOF:'):
        return

    header = f"# PROOF: [L2/Mekhane] <- {filepath} Automated PROOF header addition\n"
    with open(filepath, 'w') as f:
        f.write(header + content)
    print(f"Added PROOF header to {filepath}")

def main():
    target_dir = 'mekhane'
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                add_proof_header(filepath)

if __name__ == '__main__':
    main()

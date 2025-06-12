# Onchain AI Agent with RAG and Memory

Create a powerful AI agent capable of interacting with smart contracts on the Metis Sepolia testnet using Alith's framework. This agent supports:

- ERC20 balance checking
- Token insights
- Memory of previous interactions
- Knowledge retrieval via RAG (Retrieval-Augmented Generation)

---

## Features

- **ERC20 Token Balance Checker**: Fetch balance and metadata from any ERC20 token on Metis Sepolia.
- **Memory-Enabled Conversations**: Remembers past user interactions for context.
- **Knowledge Base (RAG)**: Leverages local knowledge about Metis, ERC20 tokens, best practices, etc.
- **Onchain Agent using **[**Alith**](https://github.com/0xLazAI/alith): Connects OpenAI-like models with blockchain agents.

---

## Installation

```bash
# Clone this repo and navigate into it
git clone https://github.com/metis-edu/Onchain-Agent-RAG-with-Memory.git
cd your-repo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install required packages
pip install alith web3 python-dotenv
```

If using vector storage:

```bash
pip install pymilvus
```

---

## Environment Setup

Create a `.env` file in the root directory:

```env
API_KEY=your_openai_api_key  # Required by Alith
```

---

## Run the Agent

```bash
python rag.py
```

### Commands Available:

```
check <contract_address> <wallet_address>   # Check token balance
exit                                        # Exit the agent
```

The agent will:

- Connect to the Metis Sepolia RPC
- Validate addresses
- Read token name, symbol, decimals, total supply
- Format raw balance into human-readable format

Example Output:

```
Token Balance Report

Token Name: ExampleToken
Symbol: EXT
Total Supply: 1,000,000.00 EXT
Decimals: 18

Wallet: 0x412dA7...F5063
Balance: 250.00 EXT
Raw Balance: 250000000000000000000

View on Explorer:
Token: https://sepolia-explorer.metisdevops.link/token/0xDead...
Wallet: https://sepolia-explorer.metisdevops.link/address/0x412d...
```

---

## Architecture

- `Web3.py`: Interacts with ERC20 contracts
- `dotenv`: Loads secure credentials
- `Alith.Agent`: Handles prompts, memory, and knowledge
- `MilvusStore` (optional): Vector DB for semantic search
- `metis_knowledge.md`: Local markdown knowledge base for RAG

---

## Troubleshooting

### Agent Errors

- **"Failed to load api\_key from parameter or .env"**:

  - Ensure `.env` exists and contains `API_KEY`

- **"Failed to read config file" (MCP error)**:

  - Alith may require a `mcp_config.json` file (check Alith documentation or pass `mcp_config_path` explicitly)

### RAG Disabled

- If `pymilvus` is not installed or the connection fails, fallback mode is used

### Token Errors

- Ensure the token address is deployed and follows the ERC20 standard
- Check RPC node availability

---

## Telegram Bot Integration

Refer to `tg-bot.py` in the repository to:

- Deploy ERC20, ERC721, or ERC1155 tokens
- Manage balances through chat
- Use natural language queries such as:
  - "Check balance for 0x123... and 0x456..."
  - "Deploy ERC20 token"

---

## Resources

- [Metis Sepolia Explorer](https://sepolia-explorer.metisdevops.link)
- [OpenAI API](https://platform.openai.com)
- [Alith Framework](https://github.com/0xLazAI/alith)
- [Python Telegram Bot Documentation](https://python-telegram-bot.readthedocs.io/)

---

## Acknowledgements

Developed using the Alith framework by LazAI and Web3.py on Metis Sepolia.

---

